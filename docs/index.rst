LibPttea 
========================

|version| |pyversions| |licence|

.. |version| image:: https://img.shields.io/pypi/v/libpttea?label=stable
   :target: https://pypi.org/project/libpttea/#history

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/libpttea
   :target: https://pypi.org/project/libpttea

.. |licence| image:: https://img.shields.io/github/license/bubble-tea-project/libpttea
   :target: https://github.com/bubble-tea-project/libpttea/blob/main/LICENSE


| LibPttea 是一個提供各種常用 PTT 功能的 Python library，例如：取得文章列表、讀取文章等。
| 此 Library 的實作基於 Python Standard Library 的 `asyncio`_ 。

.. _asyncio: https://docs.python.org/3/library/asyncio.html


以下是一個基於 `asyncio`_ 的使用範例:

.. code-block:: python

   import asyncio
   import libpttea

   PTT_ACCOUNT = "PTT ID"
   PTT_PASSWORD = "PTT 密碼"

   async def main():

      lib_pttea = await libpttea.login(PTT_ACCOUNT,PTT_PASSWORD)

      system_info = await lib_pttea.get_system_info()
      print(system_info)
      # ['您現在位於 批踢踢實業坊 (140.112.172.11)', 
      # '系統負載: 輕輕鬆鬆', 
      # '線上人數: 27492/175000', 
      # 'ClientCode: 02000023', 
      # '起始時間: 10/20/2024 05:15:40', 
      # '編譯時間: Sun Jun  4 23:41:30 CST 2023', 
      # '編譯版本: https://github.com/ptt/pttbbs.git 0447b25c 8595c8b4 M']
      
      await lib_pttea.logout()

   # run the coroutine 
   asyncio.run(main())


讓我們開始吧! :doc:`Getting started <getting_started>`



.. toctree::
   :hidden:

   install
   getting_started
   example/index
   reference/index





