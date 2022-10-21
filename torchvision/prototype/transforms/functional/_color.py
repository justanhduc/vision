import torch
from torchvision.prototype import features
from torchvision.transforms import functional_pil as _FP, functional_tensor as _FT

from ._meta import _rgb_to_gray, get_dimensions_image_tensor, get_num_channels_image_tensor


def _blend(image1: torch.Tensor, image2: torch.Tensor, ratio: float) -> torch.Tensor:
    ratio = float(ratio)
    fp = image1.is_floating_point()
    bound = 1.0 if fp else 255.0
    output = image1.mul(ratio).add_(image2, alpha=(1.0 - ratio)).clamp_(0, bound)
    return output if fp else output.to(image1.dtype)


def adjust_brightness_image_tensor(image: torch.Tensor, brightness_factor: float) -> torch.Tensor:
    if brightness_factor < 0:
        raise ValueError(f"brightness_factor ({brightness_factor}) is not non-negative.")

    _FT._assert_channels(image, [1, 3])

    fp = image.is_floating_point()
    bound = 1.0 if fp else 255.0
    output = image.mul(brightness_factor).clamp_(0, bound)
    return output if fp else output.to(image.dtype)


adjust_brightness_image_pil = _FP.adjust_brightness


def adjust_brightness_video(video: torch.Tensor, brightness_factor: float) -> torch.Tensor:
    return adjust_brightness_image_tensor(video, brightness_factor=brightness_factor)


def adjust_brightness(inpt: features.InputTypeJIT, brightness_factor: float) -> features.InputTypeJIT:
    if isinstance(inpt, torch.Tensor) and (torch.jit.is_scripting() or not isinstance(inpt, features._Feature)):
        return adjust_brightness_image_tensor(inpt, brightness_factor=brightness_factor)
    elif isinstance(inpt, features._Feature):
        return inpt.adjust_brightness(brightness_factor=brightness_factor)
    else:
        return adjust_brightness_image_pil(inpt, brightness_factor=brightness_factor)


def adjust_saturation_image_tensor(image: torch.Tensor, saturation_factor: float) -> torch.Tensor:
    if saturation_factor < 0:
        raise ValueError(f"saturation_factor ({saturation_factor}) is not non-negative.")

    c = get_num_channels_image_tensor(image)
    if c not in [1, 3]:
        raise TypeError(f"Input image tensor permitted channel values are {[1, 3]}, but found {c}")

    if c == 1:  # Match PIL behaviour
        return image

    return _blend(image, _rgb_to_gray(image), saturation_factor)


adjust_saturation_image_pil = _FP.adjust_saturation


def adjust_saturation_video(video: torch.Tensor, saturation_factor: float) -> torch.Tensor:
    return adjust_saturation_image_tensor(video, saturation_factor=saturation_factor)


def adjust_saturation(inpt: features.InputTypeJIT, saturation_factor: float) -> features.InputTypeJIT:
    if isinstance(inpt, torch.Tensor) and (torch.jit.is_scripting() or not isinstance(inpt, features._Feature)):
        return adjust_saturation_image_tensor(inpt, saturation_factor=saturation_factor)
    elif isinstance(inpt, features._Feature):
        return inpt.adjust_saturation(saturation_factor=saturation_factor)
    else:
        return adjust_saturation_image_pil(inpt, saturation_factor=saturation_factor)


def adjust_contrast_image_tensor(image: torch.Tensor, contrast_factor: float) -> torch.Tensor:
    if contrast_factor < 0:
        raise ValueError(f"contrast_factor ({contrast_factor}) is not non-negative.")

    c = get_num_channels_image_tensor(image)
    if c not in [1, 3]:
        raise TypeError(f"Input image tensor permitted channel values are {[1, 3]}, but found {c}")
    dtype = image.dtype if torch.is_floating_point(image) else torch.float32
    grayscale_image = _rgb_to_gray(image) if c == 3 else image
    mean = torch.mean(grayscale_image.to(dtype), dim=(-3, -2, -1), keepdim=True)
    return _blend(image, mean, contrast_factor)


adjust_contrast_image_pil = _FP.adjust_contrast


def adjust_contrast_video(video: torch.Tensor, contrast_factor: float) -> torch.Tensor:
    return adjust_contrast_image_tensor(video, contrast_factor=contrast_factor)


def adjust_contrast(inpt: features.InputTypeJIT, contrast_factor: float) -> features.InputTypeJIT:
    if isinstance(inpt, torch.Tensor) and (torch.jit.is_scripting() or not isinstance(inpt, features._Feature)):
        return adjust_contrast_image_tensor(inpt, contrast_factor=contrast_factor)
    elif isinstance(inpt, features._Feature):
        return inpt.adjust_contrast(contrast_factor=contrast_factor)
    else:
        return adjust_contrast_image_pil(inpt, contrast_factor=contrast_factor)


def adjust_sharpness_image_tensor(image: torch.Tensor, sharpness_factor: float) -> torch.Tensor:
    num_channels, height, width = get_dimensions_image_tensor(image)
    if num_channels not in (1, 3):
        raise TypeError(f"Input image tensor can have 1 or 3 channels, but found {num_channels}")

    if sharpness_factor < 0:
        raise ValueError(f"sharpness_factor ({sharpness_factor}) is not non-negative.")

    if image.numel() == 0 or height <= 2 or width <= 2:
        return image

    shape = image.shape

    if image.ndim > 4:
        image = image.reshape(-1, num_channels, height, width)
        needs_unsquash = True
    else:
        needs_unsquash = False

    output = _blend(image, _FT._blurred_degenerate_image(image), sharpness_factor)

    if needs_unsquash:
        output = output.reshape(shape)

    return output


adjust_sharpness_image_pil = _FP.adjust_sharpness


def adjust_sharpness_video(video: torch.Tensor, sharpness_factor: float) -> torch.Tensor:
    return adjust_sharpness_image_tensor(video, sharpness_factor=sharpness_factor)


def adjust_sharpness(inpt: features.InputTypeJIT, sharpness_factor: float) -> features.InputTypeJIT:
    if isinstance(inpt, torch.Tensor) and (torch.jit.is_scripting() or not isinstance(inpt, features._Feature)):
        return adjust_sharpness_image_tensor(inpt, sharpness_factor=sharpness_factor)
    elif isinstance(inpt, features._Feature):
        return inpt.adjust_sharpness(sharpness_factor=sharpness_factor)
    else:
        return adjust_sharpness_image_pil(inpt, sharpness_factor=sharpness_factor)


adjust_hue_image_tensor = _FT.adjust_hue
adjust_hue_image_pil = _FP.adjust_hue


def adjust_hue_video(video: torch.Tensor, hue_factor: float) -> torch.Tensor:
    return adjust_hue_image_tensor(video, hue_factor=hue_factor)


def adjust_hue(inpt: features.InputTypeJIT, hue_factor: float) -> features.InputTypeJIT:
    if isinstance(inpt, torch.Tensor) and (torch.jit.is_scripting() or not isinstance(inpt, features._Feature)):
        return adjust_hue_image_tensor(inpt, hue_factor=hue_factor)
    elif isinstance(inpt, features._Feature):
        return inpt.adjust_hue(hue_factor=hue_factor)
    else:
        return adjust_hue_image_pil(inpt, hue_factor=hue_factor)


adjust_gamma_image_tensor = _FT.adjust_gamma
adjust_gamma_image_pil = _FP.adjust_gamma


def adjust_gamma_video(video: torch.Tensor, gamma: float, gain: float = 1) -> torch.Tensor:
    return adjust_gamma_image_tensor(video, gamma=gamma, gain=gain)


def adjust_gamma(inpt: features.InputTypeJIT, gamma: float, gain: float = 1) -> features.InputTypeJIT:
    if isinstance(inpt, torch.Tensor) and (torch.jit.is_scripting() or not isinstance(inpt, features._Feature)):
        return adjust_gamma_image_tensor(inpt, gamma=gamma, gain=gain)
    elif isinstance(inpt, features._Feature):
        return inpt.adjust_gamma(gamma=gamma, gain=gain)
    else:
        return adjust_gamma_image_pil(inpt, gamma=gamma, gain=gain)


posterize_image_tensor = _FT.posterize
posterize_image_pil = _FP.posterize


def posterize_video(video: torch.Tensor, bits: int) -> torch.Tensor:
    return posterize_image_tensor(video, bits=bits)


def posterize(inpt: features.InputTypeJIT, bits: int) -> features.InputTypeJIT:
    if isinstance(inpt, torch.Tensor) and (torch.jit.is_scripting() or not isinstance(inpt, features._Feature)):
        return posterize_image_tensor(inpt, bits=bits)
    elif isinstance(inpt, features._Feature):
        return inpt.posterize(bits=bits)
    else:
        return posterize_image_pil(inpt, bits=bits)


solarize_image_tensor = _FT.solarize
solarize_image_pil = _FP.solarize


def solarize_video(video: torch.Tensor, threshold: float) -> torch.Tensor:
    return solarize_image_tensor(video, threshold=threshold)


def solarize(inpt: features.InputTypeJIT, threshold: float) -> features.InputTypeJIT:
    if isinstance(inpt, torch.Tensor) and (torch.jit.is_scripting() or not isinstance(inpt, features._Feature)):
        return solarize_image_tensor(inpt, threshold=threshold)
    elif isinstance(inpt, features._Feature):
        return inpt.solarize(threshold=threshold)
    else:
        return solarize_image_pil(inpt, threshold=threshold)


autocontrast_image_tensor = _FT.autocontrast
autocontrast_image_pil = _FP.autocontrast


def autocontrast_video(video: torch.Tensor) -> torch.Tensor:
    return autocontrast_image_tensor(video)


def autocontrast(inpt: features.InputTypeJIT) -> features.InputTypeJIT:
    if isinstance(inpt, torch.Tensor) and (torch.jit.is_scripting() or not isinstance(inpt, features._Feature)):
        return autocontrast_image_tensor(inpt)
    elif isinstance(inpt, features._Feature):
        return inpt.autocontrast()
    else:
        return autocontrast_image_pil(inpt)


def _equalize_image_tensor_vec(image: torch.Tensor) -> torch.Tensor:
    # input image shape should be [N, H, W]
    shape = image.shape
    # Compute image histogram:
    flat_image = image.flatten(start_dim=1).to(torch.long)  # -> [N, H * W]
    hist = flat_image.new_zeros(shape[0], 256)
    hist.scatter_add_(dim=1, index=flat_image, src=flat_image.new_ones(1).expand_as(flat_image))

    # Compute image cdf
    chist = hist.cumsum_(dim=1)
    # Compute steps, where step per channel is nonzero_hist[:-1].sum() // 255
    # Trick: nonzero_hist[:-1].sum() == chist[idx - 1], where idx = chist.argmax()
    idx = chist.argmax(dim=1).sub_(1)
    # If histogram is degenerate (hist of zero image), index is -1
    neg_idx_mask = idx < 0
    idx.clamp_(min=0)
    step = chist.gather(dim=1, index=idx.unsqueeze(1))
    step[neg_idx_mask] = 0
    step.div_(255, rounding_mode="floor")

    # Compute batched Look-up-table:
    # Necessary to avoid an integer division by zero, which raises
    clamped_step = step.clamp(min=1)
    chist.add_(torch.div(step, 2, rounding_mode="floor")).div_(clamped_step, rounding_mode="floor").clamp_(0, 255)
    lut = chist.to(torch.uint8)  # [N, 256]

    # Pad lut with zeros
    zeros = lut.new_zeros((1, 1)).expand(shape[0], 1)
    lut = torch.cat([zeros, lut[:, :-1]], dim=1)

    return torch.where((step == 0).unsqueeze(-1), image, lut.gather(dim=1, index=flat_image).reshape_as(image))


def equalize_image_tensor(image: torch.Tensor) -> torch.Tensor:
    if image.dtype != torch.uint8:
        raise TypeError(f"Only torch.uint8 image tensors are supported, but found {image.dtype}")

    num_channels, height, width = get_dimensions_image_tensor(image)
    if num_channels not in (1, 3):
        raise TypeError(f"Input image tensor can have 1 or 3 channels, but found {num_channels}")

    if image.numel() == 0:
        return image

    return _equalize_image_tensor_vec(image.reshape(-1, height, width)).reshape(image.shape)


equalize_image_pil = _FP.equalize


def equalize_video(video: torch.Tensor) -> torch.Tensor:
    return equalize_image_tensor(video)


def equalize(inpt: features.InputTypeJIT) -> features.InputTypeJIT:
    if isinstance(inpt, torch.Tensor) and (torch.jit.is_scripting() or not isinstance(inpt, features._Feature)):
        return equalize_image_tensor(inpt)
    elif isinstance(inpt, features._Feature):
        return inpt.equalize()
    else:
        return equalize_image_pil(inpt)


invert_image_tensor = _FT.invert
invert_image_pil = _FP.invert


def invert_video(video: torch.Tensor) -> torch.Tensor:
    return invert_image_tensor(video)


def invert(inpt: features.InputTypeJIT) -> features.InputTypeJIT:
    if isinstance(inpt, torch.Tensor) and (torch.jit.is_scripting() or not isinstance(inpt, features._Feature)):
        return invert_image_tensor(inpt)
    elif isinstance(inpt, features._Feature):
        return inpt.invert()
    else:
        return invert_image_pil(inpt)
