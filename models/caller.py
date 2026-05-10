# models/caller.py  —  Unified model caller (lazy client init)

import json, time, os, urllib.request
from typing import Optional, Dict, Any
from config import MODELS, JUDGES, OLLAMA_URL

def _get_anthropic():
    import anthropic
    return anthropic.Anthropic()

def _get_openai():
    import openai
    return openai.OpenAI()

def call_model(model_key, system, user_input, max_tokens=None, registry=None):
    reg  = registry or MODELS
    cfg  = reg[model_key]
    api  = cfg["api"]
    mid  = cfg["model_id"]
    maxt = max_tokens or cfg["max_tokens"]
    start = time.perf_counter()

    if api == "anthropic":
        client = _get_anthropic()
        kwargs = {"model":mid,"max_tokens":maxt,"messages":[{"role":"user","content":user_input}]}
        if system: kwargs["system"] = system
        resp    = client.messages.create(**kwargs)
        elapsed = round(time.perf_counter()-start, 3)
        return {"model_key":model_key,"model_id":mid,"api":api,
                "output":resp.content[0].text,
                "input_tokens":resp.usage.input_tokens,
                "output_tokens":resp.usage.output_tokens,
                "total_tokens":resp.usage.input_tokens+resp.usage.output_tokens,
                "latency_s":elapsed}

    elif api == "openai":
        client = _get_openai()
        msgs = []
        if system: msgs.append({"role":"system","content":system})
        msgs.append({"role":"user","content":user_input})
        resp    = client.chat.completions.create(model=mid,messages=msgs,max_tokens=maxt,temperature=0.0)
        elapsed = round(time.perf_counter()-start, 3)
        return {"model_key":model_key,"model_id":mid,"api":api,
                "output":resp.choices[0].message.content,
                "input_tokens":resp.usage.prompt_tokens,
                "output_tokens":resp.usage.completion_tokens,
                "total_tokens":resp.usage.total_tokens,
                "latency_s":elapsed}

    elif api == "ollama":
        msgs = []
        if system: msgs.append({"role":"system","content":system})
        msgs.append({"role":"user","content":user_input})
        payload = json.dumps({"model":mid,"messages":msgs,"stream":False,
                              "options":{"temperature":0.0,"num_predict":maxt,"num_ctx":8192}}).encode()
        try:
            req  = urllib.request.Request(OLLAMA_URL,data=payload,headers={"Content-Type":"application/json"})
            resp = urllib.request.urlopen(req,timeout=240)
            data = json.loads(resp.read())
            elapsed = round(time.perf_counter()-start,3)
            return {"model_key":model_key,"model_id":mid,"api":api,
                    "output":data["message"]["content"],
                    "input_tokens":data.get("prompt_eval_count",0),
                    "output_tokens":data.get("eval_count",0),
                    "total_tokens":data.get("prompt_eval_count",0)+data.get("eval_count",0),
                    "latency_s":elapsed}
        except Exception as e:
            return {"model_key":model_key,"model_id":mid,"api":api,
                    "output":"","input_tokens":0,"output_tokens":0,"total_tokens":0,
                    "latency_s":round(time.perf_counter()-start,3),"error":str(e)}
    else:
        raise ValueError(f"Unknown API: {api}")
