from utils.generators import IDGenerator



def test_generateID_is_deterministic():
    assert IDGenerator.generateID("test") == IDGenerator.generateID("test")


def test_generateID_different_inputs_differ():
    assert IDGenerator.generateID("a") != IDGenerator.generateID("b")


def test_generateID_returns_64_char_hex():
    result = IDGenerator.generateID("test")
    assert len(result) == 64
    int(result, 16)  # raises ValueError if not valid hex


def test_generateCHID_is_deterministic():
    chid1 = IDGenerator.generateCHID("h", "c", "a")
    chid2 = IDGenerator.generateCHID("h", "c", "a")
    assert chid1 == chid2


def test_generateCHID_order_matters():
    assert IDGenerator.generateCHID("a", "b", "c") != IDGenerator.generateCHID("b", "a", "c") 