"""One causal attention block; no dropout, biases or layer normalization."""
import torch
from torch import nn
from torch.nn import functional as F


class SmallTransformer(nn.Module):
    def __init__(self, modulus=31, embedding_dim=64, heads=4, ff_dim=128):
        super().__init__()
        self.heads = heads
        self.embedding = nn.Embedding(modulus+1, embedding_dim)
        self.position = nn.Parameter(torch.randn(3, embedding_dim)*.02)
        self.qkv = nn.Linear(embedding_dim, 3*embedding_dim, bias=False)
        self.attn_out = nn.Linear(embedding_dim, embedding_dim, bias=False)
        self.ff = nn.Sequential(nn.Linear(embedding_dim, ff_dim, bias=False), nn.ReLU(),
                                nn.Linear(ff_dim, embedding_dim, bias=False))
        self.output = nn.Linear(embedding_dim, modulus, bias=False)

    def forward(self, tokens):
        x = self.embedding(tokens) + self.position
        b, length, dim = x.shape
        qkv = self.qkv(x).reshape(b, length, 3, self.heads, dim//self.heads).permute(2,0,3,1,4)
        # Explicit attention avoids device-dependent flash-attention selection.
        q, k, v = qkv.unbind(0)
        logits = q @ k.transpose(-1,-2) / (dim//self.heads)**.5
        mask = torch.ones(length, length, device=x.device, dtype=torch.bool).triu(1)
        logits = logits.masked_fill(mask, float('-inf'))
        attn = (logits.softmax(-1) @ v).transpose(1,2).reshape(b,length,dim)
        x = x + self.attn_out(attn)
        x = x + self.ff(x)
        return self.output(x[:, -1])


def make_dataset(modulus, fraction, split_seed):
    # Independent local generator: changing init_seed cannot change the split.
    a,b = torch.meshgrid(torch.arange(modulus), torch.arange(modulus), indexing='ij')
    a,b = a.flatten(), b.flatten()
    tokens = torch.stack((a,b,torch.full_like(a,modulus)), dim=1)
    labels = (a+b) % modulus
    order = torch.randperm(len(labels), generator=torch.Generator().manual_seed(split_seed))
    n = int(len(labels)*fraction)
    if not 0 < n < len(labels):
        raise ValueError('Train fraction must produce two nonempty partitions.')
    return tokens,labels,order[:n],order[n:]
