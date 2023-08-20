import nonebot
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.message import Message
from nonebot.adapters.onebot.v11 import Bot
from sympy import symbols, nsimplify, simplify, Symbol, sympify

def lagrange_interpolation(points):
    n = len(points)
    x = symbols('x')
    result = 0
    for i in range(n):
        xi, yi = points[i]
        term = 1

        for j in range(n):
            if j != i:
                xj, _ = points[j]
                term *= (x - xj) / (xi - xj)
        result += term * yi
    return simplify(nsimplify(result))

def sEval(expr,num):
    return simplify(expr).subs(Symbol('x'),num)

li = nonebot.on_command("li",aliases={"lagrange_interpolation"})
@li.handle()
async def _(matcher: Matcher,
        bot: Bot,
        event: Event,
        args: Message = CommandArg()):
    args=args.extract_plain_text()
    args=args.split(" ")
    if len(args) > 15:
        await li.finish("Too many points! Limit: 15",at_sender=True)
    data_points = [(i+1,float(args[i])) for i in range(len(args))]
    interpolating_function = lagrange_interpolation(data_points)
    reply=["","Function:",f'f(x) = {interpolating_function}',"Points:"]
    for i in data_points:
        reply.append(f'({i[0]},{sEval(str(interpolating_function),i[0])})')
    await li.finish("\n".join(reply),at_sender=True)