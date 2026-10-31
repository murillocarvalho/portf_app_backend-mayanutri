import importlib
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
import supabase


SOURCE_DIR = Path(__file__).resolve().parents[1] / "src"


@pytest.fixture
def app_client(monkeypatch):
    fake_supabase = Mock()
    monkeypatch.setattr(
        supabase,
        "create_client",
        lambda *_args, **_kwargs: fake_supabase,
    )
    monkeypatch.syspath_prepend(str(SOURCE_DIR))
    sys.modules.pop("app", None)
    app_module = importlib.import_module("app")
    app_module.app.config["TESTING"] = True

    yield app_module.app.test_client(), fake_supabase, app_module

    sys.modules.pop("app", None)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"usuario": ""},
    ],
)
def test_insert_rejects_missing_or_empty_usuario(app_client, payload):
    client, fake_supabase, _app_module = app_client

    response = client.post("/insert", json=payload)

    assert response.status_code == 400
    assert response.get_json() == {
        "success": False,
        "message": "Campo 'usuario' obrigatório",
    }
    fake_supabase.table.assert_not_called()


def test_insert_accepts_json_and_returns_inserted_data(app_client):
    client, fake_supabase, _app_module = app_client
    inserted_data = [{"id": 1, "name": "Ana"}]
    fake_supabase.table.return_value.insert.return_value.execute.return_value = (
        Mock(data=inserted_data)
    )

    response = client.post("/insert", json={"usuario": "Ana"})

    assert response.status_code == 200
    assert response.get_json() == {
        "success": True,
        "message": "Usuário inserido com sucesso!",
        "data": inserted_data,
    }
    fake_supabase.table.assert_called_once_with("HelloWorld")
    fake_supabase.table.return_value.insert.assert_called_once_with(
        {"name": "Ana"}
    )


def test_insert_accepts_form_data(app_client):
    client, fake_supabase, _app_module = app_client
    fake_supabase.table.return_value.insert.return_value.execute.return_value = (
        Mock(data=[])
    )

    response = client.post("/insert", data={"usuario": "Ana"})

    assert response.status_code == 200
    assert response.get_json()["success"] is True
    fake_supabase.table.return_value.insert.assert_called_once_with(
        {"name": "Ana"}
    )


def test_insert_returns_database_error_details(app_client):
    client, fake_supabase, app_module = app_client
    fake_supabase.table.return_value.insert.return_value.execute.side_effect = (
        app_module.APIError(
            {"message": "Registro duplicado", "code": "23505"}
        )
    )

    response = client.post("/insert", json={"usuario": "Ana"})

    assert response.status_code == 400
    assert response.get_json() == {
        "success": False,
        "message": "Erro do Supabase/Banco de Dados",
        "error": "Registro duplicado",
        "code": "23505",
    }


def test_insert_returns_service_unavailable_on_network_error(app_client):
    client, fake_supabase, app_module = app_client
    fake_supabase.table.return_value.insert.return_value.execute.side_effect = (
        app_module.RequestError("connection failed")
    )

    response = client.post("/insert", json={"usuario": "Ana"})

    assert response.status_code == 503
    assert response.get_json() == {
        "success": False,
        "message": "Erro de rede/conexão ao comunicar com o Supabase",
        "error": "connection failed",
    }
