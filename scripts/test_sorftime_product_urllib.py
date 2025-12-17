import urllib.request
import json
import ssl

def fetch_product_details(asins, domain=1, trend=1):
    url = "https://standardapi.sorftime.com/api/ProductRequest?domain={}".format(domain)
    account_sk = "vkf3v0wwt1zpyul3m2oxswszzky0zz09"
    
    headers = {
        "Authorization": "BasicAuth {}".format(account_sk),
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0"
    }
    
    payload = []
    for asin in asins:
        payload.append({
            "ASIN": asin,
            "Trend": trend
        })
        
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    # Create an SSL context that ignores certificate verification errors (if any)
    # This is sometimes needed in restricted environments, though ideally we verify.
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            response_body = response.read().decode('utf-8')
            return json.loads(response_body)
    except urllib.error.HTTPError as e:
        print("HTTP Error: {} {}".format(e.code, e.reason))
        print(e.read().decode('utf-8'))
        return None
    except Exception as e:
        print("Error: {}".format(e))
        return None

if __name__ == "__main__":
    target_asin = "B0C135XWWH"
    print("Fetching details for ASIN: {}...".format(target_asin))
    result = fetch_product_details([target_asin])
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
