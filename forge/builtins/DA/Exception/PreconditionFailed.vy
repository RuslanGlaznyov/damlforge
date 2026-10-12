from forge.builtins import no_derive


@no_derive
struct PreconditionFailed:
    message: str
