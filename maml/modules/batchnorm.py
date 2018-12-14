import torch.nn.functional as F

from collections import OrderedDict
from torch.nn.modules.batchnorm import _BatchNorm
from torch._jit_internal import weak_module, weak_script_method
from maml.modules.module import MetaModule

@weak_module
class _MetaBatchNorm(_BatchNorm, MetaModule):
    @weak_script_method
    def forward(self, input, params=None):
        self._check_input_dim(input)
        if params is None:
            params = OrderedDict(self.named_parameters())

        exponential_average_factor = 0.0
        if self.training and self.track_running_stats:
            if self.num_batches_tracked is not None:
                self.num_batches_tracked += 1
                if self.momentum is None:  # use cumulative moving average
                    exponential_average_factor = 1.0 / float(self.num_batches_tracked)
                else:  # use exponential moving average
                    exponential_average_factor = self.momentum

        weight = params.get('weight', None)
        bias = params.get('bias', None)

        return F.batch_norm(
            input, self.running_mean, self.running_var, weight, bias,
            self.training or not self.track_running_stats,
            exponential_average_factor, self.eps)

@weak_module
class MetaBatchNorm1d(_MetaBatchNorm):
    @weak_script_method
    def _check_input_dim(self, input):
        if input.dim() != 2 and input.dim() != 3:
            raise ValueError('expected 2D or 3D input (got {}D input)'
                             .format(input.dim()))

@weak_module
class MetaBatchNorm2d(_MetaBatchNorm):
    @weak_script_method
    def _check_input_dim(self, input):
        if input.dim() != 4:
            raise ValueError('expected 4D input (got {}D input)'
                             .format(input.dim()))

@weak_module
class MetaBatchNorm3d(_MetaBatchNorm):
    @weak_script_method
    def _check_input_dim(self, input):
        if input.dim() != 5:
            raise ValueError('expected 5D input (got {}D input)'
                             .format(input.dim()))
