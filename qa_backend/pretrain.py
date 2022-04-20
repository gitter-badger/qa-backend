# AUTOGENERATED! DO NOT EDIT! File to edit: 1. Pretrain BarlowTwins.ipynb (unless otherwise specified).

__all__ = ['train']

# Internal Cell
from fastcore.script import *
from fastai.vision.all import *
from fastai.callback.wandb import *
from self_supervised.augmentations import *
from self_supervised.layers import *
from self_supervised.vision.barlow_twins import *

# fixup depreciation
from kornia import augmentation as korniatfm
korniatfm.GaussianBlur = korniatfm.RandomGaussianBlur
torch.set_num_threads(1)

# Cell
@call_parse
def train(
        path:Path, # path
        backbone:str    = 'resnet18', # backbone
        pretrained:bool = False, # pretrained
        size:int        = 224, # size
        projection_size = 2048, # projection_size
        lr:float        = 5e-4, # lr
        epochs:int      = 5, # epochs
        project:str     = None, # project
    ):
    "Pretrain a model on images in `path`."
    import wandb
    wandb.login()

    dls = ImageDataLoaders.from_name_func(path, get_image_files(path), lambda x: False, item_tfms=RandomResizedCrop(size), valid_pct=0)

    fastai_encoder = create_encoder('resnet18', pretrained=pretrained)
    model = create_barlow_twins_model(fastai_encoder, projection_size=projection_size, hidden_size=projection_size)
    aug_pipelines = get_barlow_twins_aug_pipelines(size=size, bw=False, jitter=False)
    if project is None: project = f"{path.name}-barlow-twins-pretraining"
    with wandb.init(project=project, config=dict(
        backbone=backbone, pretrained=pretrained,
        size=size, projection_size=projection_size,
        lr=lr, epochs=epochs)):
        learn = Learner(dls, model, cbs=[BarlowTwins(aug_pipelines), WandbCallback()])
        learn.fit_one_cycle(epochs, lr)
    _pretrained = "-pretrained" if pretrained else ""
    learn.save(f"barlow-twins-{backbone}{_pretrained}-{size}-{epochs}e-proj{projection_size}-lr{lr*1000}e-3",
               with_opt=False)
    return learn