from tqdm import tqdm
import os
import sys
import torch
import torch.autograd as autograd
import torch.nn.functional as F
import torch.utils.data as data
import datetime
import numpy as np

def train_model(train_data, valid_data, model, args, MAX_ACC, type):

    if args.cuda:
        model = model.cuda()

    optimizer = torch.optim.Adam(model.parameters() , lr=args.lr)

    model.train()
    temp_max_acc = 0
    for epoch in range(1, args.epochs+1):

        print("-------------\nEpoch {}:\n".format(epoch))


        loss, acc = run_epoch(train_data, True, model, optimizer, args, type)

        print('Train MSE loss: {:.6f}'.format( loss))
        print('Train MSE accuracy: {:.6f}'.format( acc))

        print()

        val_loss, val_acc = run_epoch(valid_data, False, model, optimizer, args, type)
        print('Val MSE loss: {:.6f}'.format( val_loss))
        print('Val MSE accuracy: {:.6f}'.format( val_acc))


        model.set_accuracy(val_acc)
        if model.get_accuracy() > MAX_ACC:
            MAX_ACC = model.get_accuracy()
            torch.save(model, args.save_path)
        if model.get_accuracy() > temp_max_acc:
            temp_max_acc = model.get_accuracy()

        # Save model
    return MAX_ACC, temp_max_acc

def run_epoch(data, is_training, model, optimizer, args, type):
    '''
    Train model for one pass of train data, and return loss, acccuracy
    '''
    data_loader = torch.utils.data.DataLoader(
        data,
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=True)

    losses = []
    accuracies = []

    if is_training:
        model.train()
    else:
        model.eval()

    for batch in tqdm(data_loader):

        x, y, z, a, b, labs = batch['baseX'].float(), batch['progX'].float(), batch['text'].float(), batch['token_ids'].long(), batch['segment_ids'].long(), batch['labels'].float()
        if args.cuda:
            x, y, z, a, b, labs = x.cuda(), y.cuda(), z.cuda(), a.cuda(), b.cuda(), labs.cuda()

        if is_training:
            optimizer.zero_grad()

        if type == "combined":
            out = model(x, y, z)
        elif type == "features":
            out = model(x, y)
        elif type == "bert":
            out = model(a, b)
        else:
            out = model(z)

        loss = F.mse_loss(out, labs.float())


        if is_training:
            loss.backward()
            optimizer.step()

        losses.append(loss.cpu().data[0])

        _, preds = torch.max(out, dim=1)
        _, labs = torch.max(labs, dim=1)

        accuracies.append(float(sum([preds[i]==labs[i] for i in range(preds.shape[0])]))/float(preds.shape[0]))
    # Calculate epoch level scores
    avg_loss = np.mean(losses)
    avg_acc = np.mean(accuracies)
    return avg_loss, avg_acc
