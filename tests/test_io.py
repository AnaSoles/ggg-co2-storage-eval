from storageeval import load_site_csv, simulate


def test_load_rodby_csv():
    site = load_site_csv("examples/rodby_inputs.csv", name="Rødby")
    result = simulate(site, iterations=10, seed=42)
    assert site.name == "Rødby"
    assert result.capacity_mt.shape == (10,)
