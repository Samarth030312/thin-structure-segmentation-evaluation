"""Model-zoo tests. The native MiniUNet path needs no smp/internet."""
import pytest

torch = pytest.importorskip("torch")

from uavroadmark.models import available_models, get_model  # noqa: E402


def test_miniunet_output_shape():
    model = get_model("miniunet", num_classes=7, in_channels=3)
    x = torch.randn(2, 3, 64, 64)
    y = model(x)
    assert y.shape == (2, 7, 64, 64)


def test_miniunet_handles_non_power_of_two():
    model = get_model("miniunet", num_classes=3)
    x = torch.randn(1, 3, 70, 90)
    y = model(x)
    assert y.shape[-2:] == (70, 90)


def test_registry_contains_all_required_names():
    names = set(available_models())
    for required in ["unet", "unetpp", "deeplabv3plus", "pspnet", "segformer",
                     "miniunet"]:
        assert required in names


def test_unknown_model_raises():
    with pytest.raises(KeyError):
        get_model("transformer9000")


@pytest.mark.skipif(
    pytest.importorskip is None, reason="placeholder")
def test_smp_models_if_available():
    smp = pytest.importorskip("segmentation_models_pytorch")
    assert smp is not None
    model = get_model("unet", num_classes=4, encoder="resnet18", pretrained=False)
    y = model(torch.randn(1, 3, 64, 64))
    assert y.shape == (1, 4, 64, 64)
