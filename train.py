from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

DATASET = Path(__file__).with_name("dataset")
MODEL = Path(__file__).with_name("candy_model.pt")
VAL_PHOTOS = 2
EPOCHS = 25

NORM = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])

TRAIN_TF = transforms.Compose([
    transforms.RandomRotation(180, fill=(225, 225, 225)),
    transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(0.3, 0.3, 0.2, 0.02),
    transforms.ToTensor(),
    NORM,
])

EVAL_TF = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    NORM,
])


class Crops(Dataset):
    def __init__(self, items, tf):
        self.items = items
        self.tf = tf

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        f, label = self.items[i]
        img = Image.open(f).convert("RGB")
        return self.tf(img), label


def build(n_classes):
    net = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    for p in net.parameters():
        p.requires_grad = False
    for p in net.layer4.parameters():
        p.requires_grad = True
    net.fc = nn.Linear(net.fc.in_features, n_classes)
    return net


def split(names):
    train, val = [], []
    for label, name in enumerate(names):
        groups = {}
        for f in (DATASET / name).glob("*.jpg"):
            pid = f.stem.split("_")[0]
            if pid not in groups:
                groups[pid] = []
            groups[pid].append(f)
        photos = sorted(groups)
        for pid in photos[:-VAL_PHOTOS]:
            for f in groups[pid]:
                train.append((f, label))
        for pid in photos[-VAL_PHOTOS:]:
            for f in groups[pid]:
                val.append((f, label))
    return train, val


def evaluate(net, loader, n):
    net.eval()
    confusion = torch.zeros(n, n, dtype=torch.long)
    with torch.no_grad():
        for x, y in loader:
            guesses = net(x).argmax(1)
            for truth, guess in zip(y, guesses):
                confusion[truth, guess] += 1
    return confusion.trace().item() / confusion.sum().item(), confusion


if __name__ == "__main__":
    torch.manual_seed(0)
    names = sorted(d.name for d in DATASET.iterdir() if d.is_dir())
    train, val = split(names)
    print(len(names), "classes,", len(train), "train crops,", len(val), "val crops")

    train_loader = DataLoader(Crops(train, TRAIN_TF), batch_size=16, shuffle=True)
    val_loader = DataLoader(Crops(val, EVAL_TF), batch_size=32)

    net = build(len(names))
    opt = torch.optim.Adam([
        {"params": net.fc.parameters(), "lr": 1e-3},
        {"params": net.layer4.parameters(), "lr": 1e-4},
    ])
    loss_fn = nn.CrossEntropyLoss()

    best = -1.0
    for epoch in range(1, EPOCHS + 1):
        net.train()
        seen, right, loss_sum = 0, 0, 0.0
        for x, y in train_loader:
            out = net(x)
            loss = loss_fn(out, y)
            opt.zero_grad()
            loss.backward()
            opt.step()
            loss_sum += loss.item() * len(y)
            right += (out.argmax(1) == y).sum().item()
            seen += len(y)
        val_acc, confusion = evaluate(net, val_loader, len(names))
        print(f"epoch {epoch:2d}  loss {loss_sum / seen:.3f}  train {right / seen:.0%}  val {val_acc:.0%}")
        if val_acc >= best:
            best = val_acc
            best_confusion = confusion
            torch.save({"state": net.state_dict(), "classes": names}, MODEL)

    print(f"\nbest val {best:.0%}, saved {MODEL.name}")
    print("rows = real candy, columns = what the model guessed")
    short = [n[:6] for n in names]
    print(" " * 8 + "".join(f"{s:>7}" for s in short))
    for s, row in zip(short, best_confusion.tolist()):
        print(f"{s:>8}" + "".join(f"{v:>7}" for v in row))