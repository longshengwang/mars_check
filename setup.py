from setuptools import setup, find_packages

# files = ["src/*"]


setup(
      name="mcheck",
      version="1.2",
      keywords='mars check',
      description="mars check command",
      author="Nocsys",
      author_email="wanglongshengdf@126.com",
      url="https://github.com/longshengwang/mars_check",
      license="GNU",
      python_requires='==2.7.*',
      install_requires=['requests','argcomplete'],
      packages=find_packages(),
      scripts=["script/mcheck"],
      )
