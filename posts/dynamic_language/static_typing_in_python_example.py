def python_dynamic_language_example_typed(
    execute_invalid_operation: bool,
) -> str | TypeError:
    print("The function was compiled to bytecode already")

    if execute_invalid_operation:
        a: int = 5
        b: str = "5"
        return a + b
    return "No invalid"
