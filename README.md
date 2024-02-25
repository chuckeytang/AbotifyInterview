---
title: Chatbot Advertisement Query Service
description: A service for chatbots to query relevant advertisements
tags:
  - chatbot
  - fastapi
  - asyncio
---

# 🤖 Chatbot Ad Query README

## 🌐 Understanding the Overall Business

**👉 Chatbot as a User**:  
Chatbots, acting as users, send requests to the `/get_product_info` endpoint to query for advertisements related to a specific keyword. These advertisements have not yet been shown under the management of each individual chatbot. Different chatbots manage their own list of advertisements and filter out those that have already been displayed, operating independently from each other.

## 🔍 Key Algorithm Explanation

**🌟 Relevance Algorithm for Finding Ads**:  
The core algorithm of this assessment is finding the most relevant advertisements based on search queries. A frequency-based scoring algorithm is used where the more a query keyword appears in the ad's title or content, the higher its relevance. The scoring weight for title appearances is higher (weight of 3) compared to content appearances (weight of 1). These weights can be adjusted according to business needs.

## 🧪 Test Case Function Entry

**🔬 Testing**:  
Test cases are located in `src/api/endpoints/get_product_info_test.py`. These tests should be conducted using the asyncio model.
