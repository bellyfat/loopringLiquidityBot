# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 12:30:24 2020

@author: L0GYKAL
"""

import hash_and_sign.poseidon_hash_sample.py

def sign_int_array(privateKey, serialized, t):
    PoseidonHashParams = poseidon_params(
        SNARK_SCALAR_FIELD,
        t,
        6,
        53,
        b'poseidon',
        5,
        security_target=128
    )

    hash = poseidon(serialized, PoseidonHashParams)
    signedMessage = PoseidonEdDSA.sign(hash, FQ(int(privateKey)))
    return ({
        "hash": str(hash),
        "signatureRx": str(signedMessage.sig.R.x),
        "signatureRy": str(signedMessage.sig.R.y),
        "signatureS": str(signedMessage.sig.s),
    })

def serialize_order(order):
    return [
        int(order["exchangeId"]),
        int(order["orderId"]),
        int(order["accountId"]),
        int(order["tokenSId"]),
        int(order["tokenBId"]),
        int(order["amountS"]),
        int(order["amountB"]),
        int(order["allOrNone"]=="true"),
        int(order["validSince"]),
        int(order["validUntil"]),
        int(order["maxFeeBips"]),
        int(order["buy"]=="true"),
        int(order["label"])
    ]

def sign_order(privateKey, order):
    serialized = serialize_order(order)
    signed = sign_int_array(serialized, 14 )
    order.update(signed)