# cedarkit-test-data

测试数据下载工具，为 cedarkit 系列工具套件提供测试数据准备功能。

## 安装

```bash
pip install -e .
```

## 使用方法

### 命令行

从 WIS 下载 GFS 数据：

```bash
cedarkit-test-data download gfs --source wis --output ./data
```

从本地挂载目录复制数据：

```bash
cedarkit-test-data download gfs --source music-dir --storage-base M: --output ./data
```

### Python API

```python
from cedarkit_test_data import download_gfs_data
from pathlib import Path

# 下载到指定目录
download_gfs_data(
    output_dir=Path("./data"),
    source="wis",
)
```

## 支持的数据源

- `wis`: 从 CMA WIS 数据服务下载
- `music-dir`: 从本地挂载的 music-dir 目录复制

## 支持的数据类型

- `gfs`: CMA GRAPES-GFS 全球模式数据
