from cobo_custody.config.env import Env

DEV_ENV = Env(host="https://api.dev.cobo.com",
              coboPub="03596da539963fb1dd29d5859e25903eb76b9f7ed2d58516e29c9f80c201ff2c1b")
PROD_ENV = Env(host="https://api.custody.cobo.com",
               coboPub="02c3e5bacf436fbf4da78597e791579f022a2e85073ae36c54a361ff97f2811376")