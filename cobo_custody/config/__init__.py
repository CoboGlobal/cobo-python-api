from cobo_custody.config.env import Env

SANDBOX = Env(host="https://api.sandbox.cobo.com",
              coboPub="032f45930f652d72e0c90f71869dfe9af7d713b1f67dc2f7cb51f9572778b9c876")
PROD = Env(host="https://api.custody.cobo.com",
           coboPub="02c3e5bacf436fbf4da78597e791579f022a2e85073ae36c54a361ff97f2811376")
