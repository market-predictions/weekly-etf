"""Probe guessed EUR lines directly (chart endpoint) and print name/currency."""
from v2.discover import chart
from v2 import sources as S
G = ["SXRA.DE","IUAG.AS","SUAG.AS","EUNU.DE","IS04.DE","DTLA.AS","IDTL.AS","IBTL.DE","SXRC.DE","QDVD.DE","QDVM.DE","SPMV.DE","MVUS.AS","PAVE.DE","PAVG.DE","PAVE.MI","CBUS.DE","IUSB.DE","XUTE.DE","VDTA.DE","TLTU.DE","EXX6.DE","D5BG.DE","US7.DE","3SUD.DE"]
for g in G:
    c = chart(g, days=400)
    print(f"GUESS {g} ok={c.get('ok')} cur={c.get('currency')} first={c.get('first')} name={c.get('name')}", flush=True)
    S.pause(0.3)
