<div id="readme-top"></div>

[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/contester-reborn/driver/master?logo=codefactor&logoColor=959da5&label=Code%20Quality&labelColor=333a41&color=32cb55)](https://www.codefactor.io/repository/github/contester-reborn/driver)

[//]: # (Project logo)
<br/>
<div align="center">
    <a href="https://github.com/S1riyS/TutorHub-server">
        <img src="https://i.postimg.cc/dVLsHnZy/CONTESTER-driver-logo.png" alt="Logo" width="140" height="140">
    </a>
    <h3 align="center">CONTESTER.Driver</h3>
    <p align="center">
    </p>
</div>


## 📝 About The Project

**CONTESTER.Driver** - is a Docker-based system that runs students' code written on different programming languages.

### 🐍 Avaliable programming languages:
* Python (Python 3.8)
    * PyPy (7.3.12)
* C++ (GCC Latest)
* PascalABC (Free Pascal 3.2.2)

### 🤔 How it works?
Every time user wants to execute some code `Driver` creates appropriate file and Docker container. 
Then, depending on programming language type (compiled of interpreted) it executes all necessary commands.

In order to create a file context manager `FileCreator` is invoked. Based on programming language type it will
create file with unique name and proper extension. Note that after a file is no more needed it is deleted automatically.

As for Docker containers, once again, depending on programming language type `Driver` will create `Container`. 
`Container` is a class inherited either from `CompiledContainer` or `InterpretedContainer`. 
It implements only those methods, that do something very language specific, for example return compilation or execution command.

Now, let's take a look at how `Driver` deals with source file with **C++**  code :
 
1. First of all, source code has to be compiled. To do this, `Driver` will run the following command:
    ```sh
    g++ user-scripts-dir/source-file.cpp -o compiled-files-dir/sourse-file-compiled
    ```
2. As a result, there is *sourse-file-compiled* in  a *compiled-files-dir*. Now, compiled file can be executed:
    ```sh
    sh -c 'echo -e "7 8" | time -f "%e" -o time-stdout-file timeout 2 compiled-files-dir/sourse-file-compiled && cat time-stdout-file'
    ```
  
Here are some explanations of this long command:
* `7 8` is input of the program.
* `time -f "%e" -o time-stdout-file` saves execution time in *time-stdout-file*
* `timeout 2 compiled-files-dir/sourse-file-compiled` ensures that the program is limited to 2 seconds
* `&& cat time-stdout-file`: If no error has occurred, execution time goes to the last line of stdout

After execution of this command, `Driver` will receive `ExecResult` with raw *exit code*, *stdout* and *stderr*.
Then it will thoroughly process this result and return uniform `ProcessedContainerExecutionResult` object.

Examples:
```python
ProcessedContainerExecutionResult(exit_code=0, output='1\n2\n3', execution_time=0.06, error_message='')
ProcessedContainerExecutionResult(
    exit_code=1, 
    output="""File "user-scripts-dir/62b16cbd-b2b7-44cb-8d35-7c4cf1ddd517.py", line 1
    print(
         ^
SyntaxError: '(' was never closed
Command exited with non-zero status 1""", 
    execution_time=0, 
    error_message='Run-Time Error'
)
```

More details about all those mechanisms can be found in the [source code](https://github.com/CONTESTER-reborn/driver/tree/master/driver/libs). 

✅ The vast majority of methods are documented.


## 🛠️ Technologies
* [![Python][Python-logo]][Python-link]
* [![Docker][Docker-logo]][Docker-link]


## 👍 Contributing
If you want to add new feature or suggest better solution for some aspect of this application,
you can always create a new [Pull Request](https://github.com/CONTESTER-reborn/driver/pulls).
In order to get a bug you noticed fixed create a [GitHub Issue](https://github.com/CONTESTER-reborn/driver/issues) 
and we will discuss possible solutions.

If you liked this repository, give it a 🌟 !


## 💬 Contacts

**Ankudinov Kirill** - [kirill.ankudinov.94@mail.ru](mailto:kirill.ankudinov.94@mail.ru)

My social medias:

[![telegram](https://img.shields.io/badge/-Telegram-090909?style=for-the-badge&logo=Telegram&logoColor=4F7DB3)](https://t.me/s1riysss)
[![Discord](https://img.shields.io/badge/-Discord-090909?style=for-the-badge&logo=discord)](https://discordapp.com/users/380736129361772548/)

[Python-logo]: https://img.shields.io/badge/Python-white?style=for-the-badge&logo=python
[Python-link]: https://www.python.org/
[Docker-logo]: https://img.shields.io/badge/docker-white?style=for-the-badge&logo=Docker&logoColor=white&color=blue
[Docker-link]: https://www.docker.com/