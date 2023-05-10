#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
import random
import string
import matplotlib.pyplot as plt
import os
import pandas as pd
import winsound
import time
import datetime
import math
import numpy as np


BLOCKCHAIN_CSV = "blockchain.csv"
MY_SIGNATURE = "7efc819a444d1c45c26ddb01601aca6309b413b46e317ad12c77d115afbf5b0c48b90fad209bd1a6c8dbafe227073d92e476dca4a545373dd58836daa3746703"
URL = "https://deic.uab.cat/~cborrego/block/block.php"
BLOCS_WITH_ERRORS = 0


def inicialitzar():

    print("\n----------------------------------------\
           \nStarting...")
    
    global BLOCS_WITH_ERRORS
    global BLOCKCHAIN_CSV
    global MY_SIGNATURE
    global URL

    try:
        blocs_df = pd.read_csv(os.path.join(os.path.dirname(__file__), BLOCKCHAIN_CSV))
        new = False
    except:
        blocs_df = pd.DataFrame(columns=["Block", "Hash", "Date", "Previous Hash", "Signature", "Coin", "Difficulty", "Daddy", "Time"])
        new = True

    r = requests.post(URL)
    blocs = r.text.split('<div class="center')

    for i in range(len(blocs_df)):
        try: bloc = int(blocs[i].split("Block: #")[1].split(" ")[0])
        except:
            BLOCS_WITH_ERRORS += 1
            continue
        try: date = datetime.datetime.strptime(blocs[i].split("(")[1].split(")")[0][:-3], "%d-%m-%Y %H:%M:%S")
        except:
            BLOCS_WITH_ERRORS += 1
            continue

    if new:
        inici = 0
        fi = len(blocs) + 1
    else:
        inici = len(blocs_df) + BLOCS_WITH_ERRORS 
        fi = len(blocs) + 1
    
    print("\n----------------------------------------\
           \nActualitzant Dataframe...\n")
    
    if len(blocs_df) + BLOCS_WITH_ERRORS == len(blocs):
        print("\n----------------------------------------\
               \nDataframe actualitzat!\n")
        make_plots(blocs_df)
        return blocs_df
    
    for i in range(inici, fi):
        
        try:
            bloc = int(blocs[i].split("Block: #")[1].split(" ")[0])
        except:
            BLOCS_WITH_ERRORS += 1
            continue
        
        try:
            date = datetime.datetime.strptime(blocs[i].split("(")[1].split(")")[0][:-3], "%d-%m-%Y %H:%M:%S")
            if blocs[i].split("(")[1].split(")")[0][-2:] == "pm":
                date = date + datetime.timedelta(hours=12)
            elif blocs[i].split("(")[1].split(")")[0][-2:] == "am" and date.hour == 12:
                date = date - datetime.timedelta(hours=12)
        except:
            BLOCS_WITH_ERRORS += 1
            continue
        
        previous_hash = blocs[i].split("Previous Hash: ")[-1].split("<br")[0] if "-" not in blocs[i].split("Previous Hash: ")[-1].split("<br")[0] else None
        hash = blocs[i].split("Current Hash: ")[-1].split("<br")[0]
        signature = blocs[i].split("Signature: ")[-1].split('"')[0] if " " not in blocs[i].split("Signature: ")[-1].split('"')[0] else None
        coin = blocs[i].split("Pub(")[-1].split(")")[0] if " " not in blocs[i].split("Pub(")[-1].split(")")[0] else None
        difficulty = blocs[i].split("difficulty is ")[-1].split(" bits")[0] if "difficulty is " in blocs[i] else None
        Daddy = MY_SIGNATURE == signature
        
        if not new:
            last_time = datetime.datetime.strptime(blocs_df.tail(1)["Date"].values[0], "%d-%m-%Y %H:%M:%S")
        try:
            temps = int((date - last_time).total_seconds())
            if temps < 0: temps = 0
        except: 
            temps = 0
        
        blocs_df.loc[i] = [bloc, hash, date.strftime("%d-%m-%Y %H:%M:%S"), previous_hash, signature, coin, difficulty, Daddy, temps]
        print(blocs_df.tail(1))
        last_time = date
        if new: new = not new

    # Guardem el dataframe
    blocs_df.to_csv(os.path.join(os.path.dirname(__file__), BLOCKCHAIN_CSV), index=False)
    
    print("\n----------------------------------------\
           \nDataframe actualitzat!\n")
    
    make_plots(blocs_df)
    return blocs_df


def actualitza_dataframe(blocs_df, blocs):

    global BLOCS_WITH_ERRORS
    global BLOCKCHAIN_CSV
    global MY_SIGNATURE
    global URL

    inici = len(blocs_df) + BLOCS_WITH_ERRORS 
    fi = len(blocs) + 1

    for i in range(inici, fi):
        try:
            bloc = int(blocs[i].split("Block: #")[1].split(" ")[0])
        except:
            BLOCS_WITH_ERRORS += 1
            continue
        
        try:
            date = datetime.datetime.strptime(blocs[i].split("(")[1].split(")")[0][:-3], "%d-%m-%Y %H:%M:%S")
            if blocs[i].split("(")[1].split(")")[0][-2:] == "pm":
                date = date + datetime.timedelta(hours=12)
            elif blocs[i].split("(")[1].split(")")[0][-2:] == "am" and date.hour == 12:
                date = date - datetime.timedelta(hours=12)
        except:
            BLOCS_WITH_ERRORS += 1
            continue

        last_time = datetime.datetime.strptime(blocs_df.tail(1)["Date"].values[0], "%d-%m-%Y %H:%M:%S")
        previous_hash = blocs[i].split("Previous Hash: ")[-1].split("<br")[0] if "-" not in blocs[i].split("Previous Hash: ")[-1].split("<br")[0] else None
        hash = blocs[i].split("Current Hash: ")[-1].split("<br")[0]
        signature = blocs[i].split("Signature: ")[-1].split('"')[0] if " " not in blocs[i].split("Signature: ")[-1].split('"')[0] else None
        coin = blocs[i].split("Pub(")[-1].split(")")[0] if " " not in blocs[i].split("Pub(")[-1].split(")")[0] else None
        difficulty = blocs[i].split("difficulty is ")[-1].split(" bits")[0] if "difficulty is " in blocs[i] else None
        Daddy = MY_SIGNATURE == signature

        try:
            temps = int((date - last_time).total_seconds())
            if temps < 0: temps = 0
        except:
            temps = 0

        blocs_df.loc[i] = [bloc, hash, date.strftime("%d-%m-%Y %H:%M:%S"), previous_hash, signature, coin, difficulty, Daddy, temps]
        last_time = date

    # Guardem el dataframe
    blocs_df.to_csv(os.path.join(os.path.dirname(__file__), BLOCKCHAIN_CSV), index=False)

    print("\n----------------------------------------\
           \nDataset actualitzat amb el nou bloc trobat!")
    
    return blocs_df


def make_plots(blocs_df):

    # Grafiquem un gràfic de línies de signatures

    plt.figure(figsize=(10, 5))
    # Graficamos la evolució del acomulado de bloques para cada firma en forma de linea. Top 10 signatures by number of blocs
    for signature in blocs_df["Signature"].value_counts().head(10).index:
        blocs_sing = []
        acum = 0
        for i in range(len(blocs_df)):
            if blocs_df.iloc[i]["Signature"] == signature:
                acum += 1
            blocs_sing.append(acum)
        plt.plot(blocs_sing, label=signature)
    plt.xlabel("Bloc")
    plt.ylabel("Nombre de blocs")
    plt.title("Nombre de blocs minats per adreça")
    plt.savefig(os.path.join(os.path.dirname(__file__), "blocs_per_signature.png"))
    plt.close()

    # Grafiquem la distribució del temps entre blocs

    plt.figure(figsize=(10, 5))
    plt.plot([i for i in blocs_df["Time"].values if i < 500])
    plt.xlabel("Bloc")
    plt.ylabel("Temps entre blocs")
    plt.title("Temps entre blocs")
    plt.savefig(os.path.join(os.path.dirname(__file__), "time_between_blocks.png"))
    plt.close()

    print("----------------------------------------\
           \nPlots actualitzats!\n")


def beep():
    # Reproduim un so
    duration = 1  # seconds
    freq = 440  # Hz
    # winsound.MessageBeep(winsound.MB_ICONHAND, winsound.MB_OK)
    winsound.Beep(freq, duration)


def minar(blocs_df):

    global BLOCS_WITH_ERRORS
    global BLOCKCHAIN_CSV
    global MY_SIGNATURE
    global URL

    while True:
        random_string_length = 10
        random_string = "".join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(random_string_length)
        )

        major_bloc = int(max(blocs_df["Block"]))
        last_hash = blocs_df.loc[blocs_df["Block"] == major_bloc]["Hash"].values[0]

        params = {
            "block": major_bloc + 1,
            "prev": last_hash,
            "nonce": random_string,
            "data": "[>be907d950d94e5b5c6cd4517b9f7ba14b33bc4c8a3be\
                26d077047988b33dd820(33)]7efc819a444d1c45c26ddb0160\
                1aca6309b413b46e317ad12c77d115afbf5b0c48b90fad209bd\
                1a6c8dbafe227073d92e476dca4a545373dd58836daa3746703-Daddy:)"
            # "data": "[be907d950d94e5b5c6cd4517b9f7ba14b33bc4c8a3be26d0\
            #     77047988b33dd820>e7969c9244d083a1bef385651a96454d052a3\
            #     5d4fb5912cb3fa4900780a7c980(33)]6ea7e30651cc488fe8c958\
            #     1839a61a08b3266a225e3472ee6c589e2a474d97f1634e1a7ce8c8\
            #     98d005024d8410855e08df65c85d9ce461181bc15e13ab7c4709"
            # "data": "[Hola, amigos de la blockchain!:)"
        }

        r = requests.post(URL, data=params)
        blocs = r.text.split('<div class="center')

        print("OK!")

        if len(blocs) > len(blocs_df) + BLOCS_WITH_ERRORS:

            blocs_df = actualitza_dataframe(blocs_df, blocs)

            bloc = max(blocs_df["Block"])
            count_garri = sum(blocs_df["Daddy"] == True)
            signatures = {}
            for i in blocs_df["Signature"].unique():
                if i != None and i != " " and i != "":
                    signatures[i] = sum(blocs_df["Signature"] == i)
            coins = {}
            for i in blocs_df["Coin"].unique():
                if i != None and i != " " and i != "":
                    coins[i] = (blocs_df["Coin"] == i).sum()
            count_garri_last_10 = sum(blocs_df.tail(10)["Daddy"] == True)
            adreses_with_0_coins = blocs_df[(blocs_df["Coin"].isnull()) & (blocs_df["Signature"].notnull()) & (blocs_df["Signature"] != "")]["Signature"].unique()
            difficulty = blocs_df.loc[blocs_df["Block"] == bloc, "Difficulty"].values[0]
            hash = blocs_df.loc[blocs_df["Block"] == bloc, "Hash"].values[0]
            previous_hash = blocs_df.loc[blocs_df["Block"] == bloc, "Previous Hash"].values[0]
            signature = blocs_df.loc[blocs_df["Block"] == bloc, "Signature"].values[0]
            coin = blocs_df.loc[blocs_df["Block"] == bloc, "Coin"].values[0]
            Daddy = blocs_df.loc[blocs_df["Block"] == bloc, "Daddy"].values[0]
            date = blocs_df.loc[blocs_df["Block"] == bloc, "Date"].values[0]
            temps = blocs_df.loc[blocs_df["Block"] == bloc, "Time"].values[0]

            print("\n###################################################")
            print("Bloc: ", bloc)
            print("Hash: ", hash)
            print("Date: ", date)
            print("Previous Hash: ", previous_hash)
            print("Signature: ", signature)
            print("Coin: ", coin)
            print("Difficulty: ", difficulty)
            print("Daddy: ", Daddy)
            print("Time: ", temps)
            print("Temps mitjà per bloc: ", blocs_df["Time"].mean())
            print("Daddy has mined ", count_garri, " blocks")
            print("Daddy has mined ", count_garri_last_10, " blocks in the last 10")
            print("Adresses with 0 coins mined: ", len(adreses_with_0_coins))
            print("Signatures:")
            for i, sign in enumerate(sorted(signatures.items(), key=lambda x: x[1], reverse=True)[:5]):
                print(i + 1, ". ", sign[0], "-", sign[1])
            print("Coins:")
            for i, coin in enumerate(sorted(coins.items(), key=lambda x: x[1], reverse=True)[:5]):
                print(i + 1, ". ", coin[0], "-", coin[1])
            print("###################################################\n")

            make_plots(blocs_df)
            beep()


if __name__ == "__main__":

    blocs_df = inicialitzar()
    minar(blocs_df)