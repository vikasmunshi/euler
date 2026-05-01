#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 307: Chip Defects.

Problem Statement:
    k defects are randomly distributed amongst n integrated-circuit chips
    produced by a factory (any number of defects may be found on a chip and
    each defect is independent of the other defects).

    Let p(k, n) represent the probability that there is a chip with at least
    3 defects. For instance p(3,7) ≈ 0.0204081633.

    Find p(20,000, 1,000,000) and give your answer rounded to 10 decimal places
    in the form 0.abcdefghij.

URL: https://projecteuler.net/problem=307
"""
from typing import Any

euler_problem: int = 307
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 3, 'n': 7}, 'answer': None},
    {'category': 'main', 'input': {'k': 20000, 'n': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'k': 200000, 'n': 1000000}, 'answer': None},
]
encrypted: str = (
    'ki/rqiOhK3C6nb/LBEKeSaPHmPIeGVWrtzAKmaoERedzd/FYVWRwYpj/5fTPEc9SYSzEY0iSB96qfCel'
    'wIDheOGCW6S8D4TPulufeq5nCUwWHpEtAVdjXGI307ayIZZ4VdMZJfq6pcFMcU/67gbZrHGamRVOrshx'
    'G354Un9IIGHaIH5RcIPr8GkmZ2di8pCbPKe1XaN5ByrZgUG/689IB7kFDwLAa1eVQ3ZIp4mU9DM/Soy8'
    'kYD7LUBBEvm2cM/kWCPSPDHcV0uTPJ7vyaRj2T/j8iZObPiMdk5wzu2sZHtO0rdhDGY+gbN7QNfPJHL+'
    'CHEZOaNmnQ7TNtSF8+GMwLw7n+nnE/9OBhI6FC0FEtwbgn20+cWUExwxK6Rf5AZ3nOcRaGKKSuWQt33y'
    'QjmTflp7k+uBvGordnPHO4H8oSsAqKufbOxbIwl8LjXA3ulByT7X7Bw8yMyfuJ/gO+ViJsm0AQFTXL/X'
    '/NOhrTnK4y3gvJSJhnaU0KtEeT+1Mc3/5W7BhH7/7o++HzFdt26ljunAeccdqGkpekU7mroymbA+L289'
    'cjcYJvn7bo/qu1r/M/1hFWYhuRIbvu5rrzB8dFCb+T5lb4MaCZJVIiJweL+hIYpUE9USRBS0KNNMNt24'
    '3dOU5Ls5zr3U4MreMqGHleBtrZLXawWt62f+nU1Qj5rAfOCfEEfW4ZG9EFNEW/Yt0hmfWNVxR/9Ye7mG'
    'MbDRJWyFI8iy0SMTv2MGpxuNJ3BAGQQca7+gCE4Mi3eFxBdtXxC5aZC/BGLwvzf8TRPgigKZFtIimCc6'
    'GUkksngYqd7U840vYaVvm+sdchCtiiaIGgYGryQ74EtOGO3U4uRjmTcqGqxihTZtTU9JHbFw15Jqoxj5'
    'FKnqdMmYxlkmYTodbjn810mM1VpDvrFlDgxTTvVFhucUBD7mp/7Z860Pg4A+DJOj01o6Me1gUCbbL1M1'
    'g/z4NuaM2uso84sasAx3FJhGEmHVEP7sD1KE4uhSdQn587FODVSWAo73haTRY1hhbZCEROYEytryh8gl'
    'defI+3wM7MPdnUuoSz4uHEAvnT6ouRrHlNsAmkxrme+xOLTgCJuYlahxc84ctoFgbvZjhg7MnkY1c4fw'
    'Gf7BBSEuzN5wfqggCUxigTwOgpOO1p0cZb8qqu5vwSek5lNctpURaXO6cOjPfQbJEoKJPa8MVjlG6HTg'
    'zk221KO529gbFZxZ03BfafCSWh8Lonor/qEpv7m3XQGwnEHciph4aUaLO7arPw+w24D5ILlQwK59vGay'
    '1vKzUspNnrQTWuus1XJF585GgZEver/u4rBIrx/hzNarxtOFJBj+SqAI52J0gH8IAhzFRBy1+WeHZ+lI'
    '3EjqhZTnangOsO/CQxQfGkotO/BdrJcc02HZ8NTwRNtZdbILSgjfINFqLWp8jc3hVuTb5LzmPKUUQc9D'
    'pt10rBVpudE/L/pSkSmEcFZyg/1CtsaGmAlPVJic1VZHfSQ+OBKooeh4SyJAxWpWjJMGvQAETDD/IhCh'
    'Gvo7MkI1alrBkDMJ/v4AEaRL1Lj7OB1nExpUPXGW07UT3quWCPuVuqfuNXSUO/zA2FxpEeXEzd4hI+7j'
    'gyh3qVTbSCBHNFQviWLuk5BRbObAkhVScnqzZEQZ0v26G9Gg3dYmXtFmvM4ujRrvlddbimJ928AR5SQ4'
    '7pG7gBAFRDh3k8lUDHkbh4PxojImE4h8jNhnSFO6wM8NKGJR0QuI8+E/T51gZ7jr+xHGURzz7WeSArrc'
    'MB1rJHjTyIql7ihyozT78MS+mmBZ4ZnWWbkMOg21ZrYsLjWjGPGDIVjed8jv8Vr//ovS71x327fQC7xP'
    'wt3ZwfrxYT/wfRDay03cN50RKIX4Ui/l/ghhU6lHQ21zuRdfFPOGMhUwZEegSz3QAcyFQgCPr61BP79A'
    'KZtIXU768K1ystklqLgizzAUyAxzXiskftFSaejQFcAfVT2d13yKhqCU2N8r9b3ILuU2PnBpWHaK+GDP'
    'p96hJ/18i0t6mJdCV5rctNojwqkTS0A5atNK43FYC1pgMhIuEXU6uHKqlUnbQDgI+AcagGT5kkW9+L+s'
    'kLgEAjFhDk/6qiLn7ocpCE8tETqIh6Nu1X0xRUbhww8GkVMx0ppgUQpO0gwHxQQ/Wa29vO2g2YGhqfv3'
    '04gThD6Mz5r7O4bWKJXg2Hs8DaMiUXFx7jUN1uasN2mqjJl9fAQuRWiMgtTNnXMwu8l7g3XybNyXSiRI'
    'gnxIJREUEWVhe2JU6dFjSuSAiPi1Jixx7H2V69j31r2TfEjx7rGMTeaOmnDhiRgT2d/oJPhQiKNm2rwF'
    'vdJcvS+ZNdhSzLxwE8qfP/UvRMAAuzrXN9HE0uPYgTMSGIEKW96GVnwDuMJ5wzhVqcXqTzkLtOXX3u65'
    '/MQKWw2TypoiBNXD76qmA0Zmt8OuCz6bf/XvfiIKiyzeHwukdDGK9ASJ6Kb95nJSR09CkWwM2stSSnBK'
    '0aHjB3JAQVWV0keEtn7zSnqEwX+j9Cd/1Wpsef1lg8T9AQynQ870uJTNY9T66S0suRsTIzbsMN85eEH0'
    'CP7G7gqKYRAHXSLOlBQzhfwi7fXUVGGBN6Jc+r0Iyvgu6jFOhJZUBVNfrmR5kCOvP+bek1dBdiGPuFXS'
    'EJCY2Q=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
