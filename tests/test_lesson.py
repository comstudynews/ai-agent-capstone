from app.lesson import run

def test_all_recipe_checkpoints():
    for number in range(1, 16):
        result = run(number)
        assert isinstance(result, dict) and result
