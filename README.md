# 人脸拼接小工具

## 特性

### 左右拼接
<center>
    <img src="./output/joint.png">
</center>

### 上下拼接

<center>
    <img src="./output/5.jpg"  width="400">
</center>

## 依赖

- 安装 [face_recognition](https://github.com/ageitgey/face_recognition#installation-options)

- `pip3 install -r requirements.txt`

## 使用

- 左右拼接

    `python3 face.py -l left.jpg -r right.jpg -o output.jpg `

- 上下拼接

    `python3 face.py -l upside.jpg -r downside.jpg -o output.jpg `

- `python3 face.py -h`

    ```text
    usage: face.py [-h] [-l LEFT] [-r RIGHT] [-u UPSIDE] [-d DOWNSIDE] [-o OUTPUT]
    
    face cut & concat tool
    
    optional arguments:
      -h, --help            show this help message and exit
      -l LEFT, --left LEFT  face on the left
      -r RIGHT, --right RIGHT
                            face on the right
      -u UPSIDE, --upside UPSIDE
                            face on the upside
      -d DOWNSIDE, --downside DOWNSIDE
                            face on the downside
      -o OUTPUT, --output OUTPUT
                            save concat image
    
    ```
    
## License

MIT @ [github/wangshub](https://github.com/wangshub)