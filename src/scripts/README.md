## Sample Commands
run from GPTS-ADS-BACKEND folder:

## Main commands

### Add a Creator 
```shell
python3 -m src.scripts.creator.add_creator --email "first_creator@proton.me"
```
### Add a chatbot
```shell
python3 -m src.scripts.chatbot.add_chatbot "first_chatbot" --source "openai_gpts" --link "https://firs_chatbot.com" --amazon_product_key "key" --creator_username "first_creator”
```
Note: amazon_product_key is just the tracking id, it's better to create a new one on the amazon affiliate website. 

python3 -m src.scripts.chatbot.add_chatbot "markusmak1" --source "openai_gpts" --link "https://firs_chatbot.com" --amazon_product_key "markusmak1-20" --creator_username "MarkusMak"


## Other creator commands

### Get a Creator given username
```shell
python3 -m src.scripts.creator.get_creator "first_creator"
```

### Update a Creator 
```shell
python3 -m src.scripts.creator.update_creator "first_creator" --name "first_creator" --email "first_creator@proton.me"
```

### Remove a Creator 
```shell
python3 -m src.scripts.creator.remove_creator "first_creator"
```


## Chatbot commands



### Get a chatbot
```shell
python3 -m src.scripts.chatbot.get_chatbot "<api_key>"
```

### Update a chatbot
```shell
python3 -m src.scripts.chatbot.update_chatbot "<api_key>" --source "openai_assistant"
```

### Remove a chatbot
```shell
python3 -m src.scripts.chatbot.remove_chatbot "<api_key>"
```