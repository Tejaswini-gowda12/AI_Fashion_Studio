import numpy as np

class TemperatureScaler:
    """
    Calibrates neural network raw logits using Temperature Scaling
    so predicted probabilities match empirical validation accuracy.
    """
    def __init__(self, temperature: float = 1.25):
        self.temperature = max(0.5, temperature)

    def calibrate(self, logits: np.ndarray) -> np.ndarray:
        """
        Applies temperature scaling to raw logits before softmax.
        """
        scaled_logits = logits / self.temperature
        exp_logits = np.exp(scaled_logits - np.max(scaled_logits))
        probabilities = exp_logits / np.sum(exp_logits)
        return probabilities
