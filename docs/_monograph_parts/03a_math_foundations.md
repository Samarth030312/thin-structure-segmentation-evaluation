# Part 3 — Mathematical Foundations

This part builds every mathematical tool the project uses, from vectors to the loss
functions and metrics. For each concept you get **(1) intuition, (2) a derivation or
definition, (3) a small numerical example, (4) why it matters here.** Read with a
pencil.

## 3.1 Vectors

**Intuition.** A vector is an ordered list of numbers. A pixel's RGB colour is a
3-vector `[r, g, b]`. A class-score output is a `C`-vector.

**Definition.** `x = (x₁, …, x_n) ∈ ℝⁿ`. Key operations: addition (elementwise),
scalar multiply, and the **dot product** `x·y = Σᵢ xᵢyᵢ`, which measures alignment.

**Example.** `x = [1, 2, 0]`, `y = [0, 2, 3]` → `x·y = 1·0 + 2·2 + 0·3 = 4`.

**Project relevance.** Every pixel's prediction is a `C`-vector of class scores; the
dot product underlies both convolution and the linear layers that produce those
scores.

## 3.2 Matrices and linear transformations

**Intuition.** A matrix is a grid of numbers that, when multiplied by a vector,
*transforms* it — rotating, scaling, projecting. Neural-network layers are (mostly)
matrices.

**Definition.** `A ∈ ℝ^{m×n}` maps `ℝⁿ → ℝᵐ` via `y = Ax`, with
`yᵢ = Σⱼ Aᵢⱼ xⱼ`. Composition of linear maps is matrix multiply: `(AB)x = A(Bx)`.

**Example.** Scale-x-by-2:
`A = [[2,0],[0,1]]`, `x = [3,5]` → `Ax = [6,5]`.

**Project relevance.** A convolution is a *special structured* matrix multiply (a
matrix that shares weights and is mostly zeros). The final `1×1` convolution that
produces class scores is literally a per-pixel matrix-vector product.

## 3.3 Tensors and how images are represented

**Intuition.** A tensor is an `n`-dimensional array — the generalisation of
scalar (0-D), vector (1-D), matrix (2-D) to 3-D, 4-D, …

**Definition / conventions.** In PyTorch:
- an image is `(C, H, W)` — channels, height, width;
- a *batch* of images is `(N, C, H, W)`;
- a segmentation label map is `(H, W)` of integers, or `(N, H, W)`;
- a model's per-class scores ("logits") are `(N, C, H, W)`.

**Example.** A `256×256` RGB image is a `(3, 256, 256)` tensor = 196 608 numbers. A
batch of 4 is `(4, 3, 256, 256)`.

**Project relevance.** Memory is the binding constraint on a 4 GB GPU. A `(4, 3,
512, 512)` input is small, but the *intermediate feature tensors* inside a U-Net are
huge (dozens of `(N, 256, 128, 128)` activations), which is why batch size had to
stay tiny (Part 11).

## 3.4 Convolution — the core operation of CV

**Intuition.** Slide a small window (a **kernel**) over the image. At each position,
multiply the kernel by the patch underneath and sum. The kernel is a little pattern
detector: an edge kernel lights up at edges, a blur kernel averages.

**Definition (2-D, single channel).** For input `X` and kernel `K` of size `k×k`,
the output (feature map) is

$$Y[i,j] \;=\; \sum_{a=0}^{k-1}\sum_{b=0}^{k-1} K[a,b]\; X[i+a,\; j+b].$$

(Strictly this is *cross-correlation*; deep-learning "convolution" uses this form.)
With `C_in` input channels and `C_out` filters, the kernel is `(C_out, C_in, k, k)`
and each output channel sums over all input channels.

**Numerical example.** Vertical-edge (Sobel) kernel
`K = [[-1,0,1],[-2,0,2],[-1,0,1]]` on a patch that is dark-left / bright-right gives
a large positive response; on a flat patch it gives 0. That is edge detection in one
multiply-add.

**Why convolution and not a full matrix?** Two reasons:
- **Weight sharing:** the same kernel is used at every location → far fewer
  parameters and *translation equivariance* (an edge is an edge wherever it is).
- **Locality:** each output depends only on a small input neighbourhood → matches the
  local structure of images.

**Project relevance.** Every architecture here (U-Net, DeepLab, SegFormer's early
stages) is a stack of convolutions. The "thin marking" the network must find is a
local oriented pattern — exactly what convolutions detect.

## 3.5 Feature maps, padding, stride, receptive field

- **Feature map:** the output tensor of a conv layer; channel `c` is a map of "how
  strongly filter `c` fired at each location."

- **Padding:** add a border of zeros so the output keeps the input size. Without
  padding, a `k×k` conv shrinks the map by `k−1`. "Same" padding (`p=(k−1)/2`) keeps
  `H×W` fixed — important for segmentation, where output must match input size.

- **Stride `s`:** move the kernel `s` pixels at a time. `s=2` halves the resolution
  (downsampling). Output size: `⌊(H + 2p − k)/s⌋ + 1`.

  *Example:* `H=256, k=3, p=1, s=2 → (256+2−3)/2+1 = 128`.

- **Receptive field:** the region of the *input* that influences one output pixel.
  It grows as you stack layers and downsample. To label a marking pixel correctly you
  often need context (where is the road?), so you need a large receptive field —
  achieved by depth, striding, pooling, dilation, or attention.

**Project relevance.** Segmentation needs *both* large receptive field (context) and
*high output resolution* (precise thin-structure localisation). These pull in
opposite directions; the architectures in Part 4 are different answers to this
tension, and thin structures punish any architecture that downsamples too
aggressively without recovering detail.

## 3.6 Nonlinearities

**Intuition.** Stacking linear layers collapses to one linear layer (`A(Bx)=(AB)x`).
To learn complex functions you insert a nonlinear function between them.

**Definition.** The **ReLU** is `relu(x) = max(0, x)` — pass positives, zero
negatives. Cheap, and its gradient is simply 1 (for `x>0`) or 0.

**Project relevance.** ReLU (and variants) sit after most convolutions. They also
create the "dead-zero" behaviour that makes deep nets sensitive to initialisation
and learning rate (Part 11 on why fp16 diverged).

## 3.7 Loss, gradient descent, and the chain rule

This is *how networks learn*. A network is a function `f_θ(x)` with parameters `θ`
(all the kernel weights). We measure error with a **loss** `L(θ)` and adjust `θ` to
reduce it.

### 3.7.1 Gradient descent
**Intuition.** The gradient `∇L` points in the direction of steepest *increase* of
the loss. Step the opposite way to go downhill.

**Rule.** `θ ← θ − η ∇_θ L`, where `η` is the **learning rate** (step size).

**Example (1-D).** `L(θ) = (θ − 3)²`. Then `L'(θ) = 2(θ−3)`. At `θ=0`, `L'=−6`, so
`θ ← 0 − η(−6) = 6η`. With `η=0.1`, `θ=0.6`, moving toward the minimum at 3. Repeat
and it converges.

### 3.7.2 The chain rule and backpropagation
**Intuition.** A network is a composition `L = ℓ(f_n(…f_1(x)))`. To get the gradient
w.r.t. an early weight, multiply the local derivatives along the path — the **chain
rule**. **Backpropagation** is just the chain rule applied right-to-left, reusing
shared sub-results so it costs about as much as one forward pass.

**Chain rule.** If `y = g(u)` and `u = h(θ)`, then
$$\frac{\partial y}{\partial \theta} = \frac{\partial y}{\partial u}\,\frac{\partial u}{\partial \theta}.$$

**Worked micro-example.** One neuron: `u = w·x`, `ŷ = relu(u)`, `L = (ŷ − t)²`.
- `∂L/∂ŷ = 2(ŷ − t)`
- `∂ŷ/∂u = 1` if `u>0` else `0`
- `∂u/∂w = x`
- chain: `∂L/∂w = 2(ŷ − t)·[u>0]·x`.

That product of three local derivatives is one backprop step. A real network does
this for millions of weights automatically (PyTorch's autograd).

### 3.7.3 Optimizers
Plain gradient descent is slow and noisy. **Adam / AdamW** keep running averages of
the gradient (momentum) and its square (adaptive per-parameter step), giving fast,
stable convergence. This project uses **AdamW** with a **cosine** learning-rate
schedule (the LR starts high and smoothly decays to 0), visible in the training logs
as `lr 7.97e-04 → … → 0.00e+00`.

**Project relevance.** Understanding LR matters: at half precision (fp16) the
gradients of the soft-skeleton operations underflowed and training **diverged to
NaN**, forcing full precision (fp32). That is a direct consequence of the
chain-rule products becoming tiny (Part 11).

## 3.8 Cross-entropy loss

**Intuition.** For classification we want the model to put high probability on the
correct class. Cross-entropy punishes confident wrong answers heavily.

**Softmax → probabilities.** Logits `z ∈ ℝ^C` become probabilities
$$p_c = \frac{e^{z_c}}{\sum_{k} e^{z_k}}.$$

**Cross-entropy.** For true class `t`,
$$L_\text{CE} = -\log p_t.$$
If the model is sure and right (`p_t→1`), `L→0`; sure and wrong (`p_t→0`), `L→∞`.

**Example.** Two classes, logits `[2.0, 0.5]` → `p = [0.82, 0.18]`. If true class is
0, `L = −log(0.82) = 0.20` (small). If true class is 1, `L = −log(0.18) = 1.71`
(large).

**For segmentation** we average CE over all pixels. **Problem for thin structures:**
98% of pixels are background, so the *average* CE is dominated by background and the
model can drive the loss down while ignoring markings. This motivates the
region/overlap losses next, and is one half of why naive training under-segments
thin structures.

---
