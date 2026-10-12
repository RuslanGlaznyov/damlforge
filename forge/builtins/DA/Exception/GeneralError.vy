from forge.builtins import no_derive


@no_derive
struct GeneralError:
    message: str
