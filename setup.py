from setuptools import setup, find_packages

# files = ["src/*"]


setup(
      name="nocsys_mars_debugtool",
      version="1.0.1",
      keywords='mars debugtool',
      description="A debug tool for debuging the Nocsys Mars Controller controlled fabric and controller itself",
      author="Nocsys",
      author_email="longsheng.wang@nocsys.com.cn",
      url="https://github.com/longshengwang/mars_check",
      license="GNU",
      python_requires='==2.7.*',
      install_requires=['requests','argcomplete'],
      packages=find_packages(),
      scripts=["script/mcheck"],
      )
