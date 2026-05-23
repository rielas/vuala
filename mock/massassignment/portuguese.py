from mock import Mock, Response
import pprint

pp = pprint.PrettyPrinter(indent=4)


class Mock(Mock):
    def __init__(self, domain: str):
        super().__init__(domain)
        self.last_user = None
        self.authorized = False


class Usuario:
    def __init__(
        self,
        email: str,
        primeiroNome: str,
        sobrenome: str,
        empresa: str,
        numeroTelefone: str,
        senha: str,
        operacao: str,
        eAdministrador: bool = False,
    ):
        self.email = email
        self.primeiroNome = primeiroNome
        self.sobrenome = sobrenome
        self.empresa = empresa
        self.numeroTelefone = numeroTelefone
        self.senha = senha
        self.operacao = operacao
        self.eAdministrador = eAdministrador


@Mock.route("/api/usuarios/basico", method="POST")
def _(self, query: dict, data: dict):
    usuario = Usuario(**data)
    self.last_user = usuario
    return Response({}, 201)


@Mock.route("/api/autenticacao/login", method="POST")
def _(self, query: dict, data: dict):
    self.authorized = False

    try:
        email = data["usuario"]
    except KeyError:
        return Response(
            {
                "erro": "Usuário não encontrado",
            },
            500,
        )

    password = data["senha"]

    if set(data.keys()) != {"usuario", "senha"}:
        return Response(
            {
                "erro": "Dados da solicitação inválidos",
            },
            500,
        )

    if self.last_user:
        user = self.last_user

        if user.email == email and user.senha == password:
            self.authorized = True
            return Response(
                {"email": user.email},
                201,
            )

    return Response(
        {
            "erro": "Usuário não encontrado",
            "local": "/var/www/dist/auth/auth.controller.js",
        },
        500,
    )


@Mock.route("/api/usuarios/um/<str:email>", method="GET")
def _(self, query: dict, data: dict, email: str):
    user = self.last_user

    if user.email == email:
        return Response(
            {
                "id": len(user.email),
                "email": user.email,
                "primeiroNome": user.primeiroNome,
                "sobrenome": user.sobrenome,
                "empresa": user.empresa,
                "numeroTelefone": user.numeroTelefone,
            },
            200,
        )

    return Response(
        {
            "erro": "Usuário não encontrado",
            "local": "/var/www/dist/auth/auth.controller.js",
        },
        500,
    )


@Mock.route("/api/usuarios/eu", method="GET")
def _(self, query: dict, data: dict):
    if not self.authorized:
        return Response(
            {"erro": "Não autorizado", "linha": "/var/www/dist/auth/auth.guard.js"},
            401,
        )

    user = self.last_user
    return Response(
        {
            "email": user.email,
            "primeiroNome": user.primeiroNome,
            "sobrenome": user.sobrenome,
            "empresa": user.empresa,
            "numeroTelefone": user.numeroTelefone,
            "operacao": user.operacao,
            "eAdministrador": user.eAdministrador,
        },
        200,
    )


def har() -> dict:
    mock = Mock("brokencrystals.com")

    assert (
        mock.make_request(
            "POST",
            "/api/usuarios/basico",
            {
                "email": "robo.ruckus@brightsec.com",
                "primeiroNome": "",
                "sobrenome": "",
                "empresa": "",
                "numeroTelefone": "",
                "senha": "000",
                "operacao": "basico",
            },
        ).status_code
        == 201
    )
    assert (
        mock.make_request(
            "POST",
            "/api/autenticacao/login",
            {"usuario": "robo.ruckus@brightsec.com", "senha": "000"},
        ).status_code
        == 201
    )

    assert (
        mock.make_request(
            "GET", "/api/usuarios/um/robo.ruckus@brightsec.com"
        ).status_code
        == 200
    )

    assert mock.make_request("GET", "/api/usuarios/eu").content["eAdministrador"] is False

    return mock.har()


def main():
    har()


if __name__ == "__main__":
    main()
