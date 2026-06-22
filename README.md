# Perceptron Demo

An animated single-layer perceptron implemented from scratch with NumPy and Matplotlib.

The script generates a linearly separable 2D dataset, trains a perceptron with the classic update rule, and opens an interactive dashboard that visualizes:

- the current decision boundary
- misclassified training samples
- the latest corrected sample
- epoch-by-epoch training accuracy and update counts

## Features

- Perceptron training with binary labels `-1` and `1`
- Reproducible synthetic dataset generation
- Interactive Matplotlib controls for learning rate and iteration count
- Visual replay of parameter updates during training

## Requirements

- Python 3.10+
- `numpy`
- `matplotlib`

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Run

```bash
python perceptron_demo.py
```

When the script finishes training, it prints the final weights, bias, and accuracy values in the terminal, then opens the dashboard window.

## Project Structure

- `perceptron_demo.py` - perceptron implementation, dataset generation, and dashboard
- `requirements.txt` - pinned Python dependencies

## Notes

- The demo uses a synthetic dataset, so no external data files are needed.
- The visualization requires a GUI-capable Python environment.
