"""Loss-function tests: scalar output, gradient flow, and sane behaviour."""
import pytest

torch = pytest.importorskip("torch")

from uavroadmark.losses import available_losses, get_loss  # noqa: E402


@pytest.fixture
def batch():
    torch.manual_seed(0)
    logits = torch.randn(2, 3, 8, 8, requires_grad=True)
    target = torch.randint(0, 3, (2, 8, 8))
    return logits, target


@pytest.mark.parametrize("name", ["ce", "dice", "focal", "tversky", "ce_dice",
                                  "focal_tversky", "lovasz"])
def test_loss_scalar_and_grad(name, batch):
    logits, target = batch
    loss = get_loss(name, ignore_index=-100)(logits, target)
    assert loss.ndim == 0
    assert torch.isfinite(loss)
    loss.backward()
    assert logits.grad is not None
    assert torch.isfinite(logits.grad).all()


def test_dice_near_zero_on_perfect_prediction():
    target = torch.randint(0, 3, (1, 8, 8))
    onehot = torch.nn.functional.one_hot(target, 3).permute(0, 3, 1, 2).float()
    logits = (onehot * 20.0)  # confident, correct logits
    loss = get_loss("dice")(logits, target)
    assert loss.item() < 0.05


def test_tversky_beta_gt_alpha_penalizes_false_negatives_more():
    # one foreground pixel; compare a false-negative vs a false-positive case
    target = torch.zeros(1, 4, 4, dtype=torch.long)
    target[0, 0, 0] = 1
    tv = get_loss("tversky", alpha=0.3, beta=0.7)
    # case A: model misses the fg pixel (false negative)
    miss = torch.zeros(1, 2, 4, 4)
    miss[:, 0] = 10.0  # predict all background
    # case B: model adds a spurious fg pixel elsewhere (false positive)
    fp = torch.zeros(1, 2, 4, 4)
    fp[:, 0] = 10.0
    fp[0, 0, 0, 0] = -10.0; fp[0, 1, 0, 0] = 10.0   # correct the real pixel
    fp[0, 0, 3, 3] = -10.0; fp[0, 1, 3, 3] = 10.0   # add a false positive
    loss_miss = tv(miss, target).item()
    loss_fp = tv(fp, target).item()
    assert loss_miss > loss_fp  # FN penalised more than FP


def test_registry_lists_all():
    names = set(available_losses())
    for expected in ["ce", "dice", "focal", "tversky", "ce_dice"]:
        assert expected in names


def test_unknown_loss_raises():
    with pytest.raises(KeyError):
        get_loss("not_a_loss")
