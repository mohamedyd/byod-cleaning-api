import os
import random
import shutil
import sys

import click
from kbclean.detection.active_transform import HoloDetector, LSTMDetector
from kbclean.detection.active_transform.random_forest import RandomForestDetector
from kbclean.evaluation import Evaluator
from kbclean.utils.inout import load_config
from loguru import logger

config = {
    "handlers": [
        {"sink": sys.stdout, "format": "{time} - {message}", "level": "INFO"},
        {
            "sink": "error.log",
            "format": "{time} - {message}",
            "level": "ERROR",
            "backtrace": True,
            "diagnose": True,
        },
        {"sink": "info.log", "format": "{time} - {message}", "level": "INFO",},
        {"sink": "debug.log", "format": "{time} - {message}", "level": "DEBUG",},
    ]
}


name2model = {
    "holo": HoloDetector,
    "lstm": LSTMDetector,
    "random_forest": RandomForestDetector,
}

logger.configure(**config)

logger.info(
    "=========================================================================="
)

random.seed(1811)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--data_path", "-d", help="Path to dataset")
@click.option(
    "--config_path", "-c", help="Path to configuration file", default="config"
)
@click.option("--output_path", "-o", help="Path to output directory", default="output")
@click.option(
    "--method", "-m", help="Method for outlier detection", default="deep_clean"
)
@click.option("--interactive", "-i", is_flag=True, help="Interactive detection")
@click.option("--start", help="Start range", default=0, type=int)
@click.option("--end", help="End range", default=None, type=int)
@click.option("--num_gpus", help="Number of GPUs used", default=1)
@click.option("-k", help="Number of iterations", default=2)
@click.option("-e", help="Number of examples per iteration", default=2)
def evaluate(
    data_path, config_path, output_path, method, interactive, start, end, num_gpus, k, e
):
    evaluator = Evaluator()

    hparams = load_config(config_path)

    detector = name2model[method](getattr(hparams, method))
    getattr(hparams, method).num_gpus = num_gpus
    getattr(hparams, method).num_examples = e

    if interactive:
        evaluator.ievaluate(
            detector, method, data_path, output_path, step=k, data_range=[start, end]
        )
    else:
        evaluator.evaluate(detector, method, data_path, output_path)


@cli.command()
def clear():
    shutil.rmtree("output", ignore_errors=True)
    os.remove("info.log")
    os.remove("error.log")
    os.remove("debug.log")


if __name__ == "__main__":
    cli()
