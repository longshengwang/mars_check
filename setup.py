from setuptools import setup, find_packages

# files = ["src/*"]


setup(
      name="nocsys_mars_debugtool",
      version="1.0.1",
      keywords='mars debugtool',
      description="A debug tool for debuging the Nocsys Mars Controller controlled fabric and controller itself",
      author="Nocsys",
      author_email="macauley.cheng@nocsys.com.cn",
      url="https://github.com/nocsysmars/mars_check",
      license="GNU",
      python_requires='>=3.*',
      install_requires=['requests','argcomplete'],
      packages=find_packages(),
      scripts=["script/marscheck"],
      )
