"""Tests for the topology-aware losses (clDice, CoRe = proposed)."""
import pytest

torch = pytest.importorskip("torch")

from uavroadmark.losses import get_loss
from uavroadmark.losses.topology import SoftSkeletonize


def _confident_logits(target, num_classes=7, scale=15.0):
    oh = torch.nn.functional.one_hot(target, num_classes).permute(0, 3, 1, 2).float()
    return oh * scale


def test_soft_skeleton_shape_and_range():
    skel = SoftSkeletonize(num_iter=5)
    img = torch.rand(2, 1, 32, 32)
    out = skel(img)
    assert out.shape == img.shape
    assert out.min() >= 0.0


@pytest.mark.parametrize("name", ["cldice", "core"])
def test_topology_loss_scalar_and_grad(name):
    torch.manual_seed(0)
    logits = torch.randn(2, 7, 32, 32, requires_grad=True)
    target = (torch.rand(2, 32, 32) > 0.85).long() * torch.randint(1, 7, (2, 32, 32))
    loss = get_loss(name)(logits, target)
    assert loss.ndim == 0 and torch.isfinite(loss)
    loss.backward()
    assert torch.isfinite(logits.grad).all()


def test_cldice_low_on_perfect_prediction():
    target = torch.zeros(1, 48, 48, dtype=torch.long)
    target[0, 20:24, 4:44] = 1  # a thick line
    logits = _confident_logits(target)
    loss = get_loss("cldice")(logits, target)
    assert loss.item() < 0.2  # near-perfect topology -> low clDice loss


def test_core_warmup_ramps_topology_weight():
    loss = get_loss("core", w_region=1.0, w_topo=1.0, warmup=10)
    loss.train()
    assert loss._topo_weight() == 0.0          # step 0
    target = torch.zeros(1, 16, 16, dtype=torch.long)
    target[0, 8, 2:14] = 1
    logits = _confident_logits(target)
    for _ in range(10):
        loss(logits, target)                    # advances internal step
    assert loss._topo_weight() == pytest.approx(1.0, abs=1e-6)  # fully ramped


def test_core_reduces_to_ce_dice_when_topo_zero():
    """With w_topo=0 and region=dice, CoRe == its CE+Dice base (no topology)."""
    torch.manual_seed(1)
    logits = torch.randn(2, 7, 24, 24)
    target = (torch.rand(2, 24, 24) > 0.8).long() * torch.randint(1, 7, (2, 24, 24))
    core = get_loss("core", w_ce=0.5, w_region=0.5, w_topo=0.0, region="dice")
    ce_dice = get_loss("ce_dice", w_ce=0.5, w_dice=0.5)
    assert core(logits, target).item() == pytest.approx(ce_dice(logits, target).item(), abs=1e-5)


def test_core_tversky_variant_runs():
    torch.manual_seed(2)
    logits = torch.randn(2, 7, 24, 24, requires_grad=True)
    target = (torch.rand(2, 24, 24) > 0.8).long() * torch.randint(1, 7, (2, 24, 24))
    loss = get_loss("core", region="tversky", alpha=0.3, beta=0.7, w_topo=0.5)(logits, target)
    assert torch.isfinite(loss)
    loss.backward()
    assert torch.isfinite(logits.grad).all()
