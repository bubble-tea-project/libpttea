"""
libpttea Library
~~~~~~~~~~~~~~

LibPttea is a Python library that encapsulates various PTT functions.

Basic usage:
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

"""

from .api import login

