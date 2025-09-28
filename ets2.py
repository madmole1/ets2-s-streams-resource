import requests
import os
import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_multiple_pages(base_url, max_pages=10):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    all_results = []  # 存储所有抓取到的卡片数据
    current_url = base_url
    page_count = 0
    seen_items = set()  # 用于去重检查

    while current_url and page_count < max_pages:
        print(f"正在抓取第 {page_count + 1} 页: {current_url}")
        try:
            response = requests.get(current_url, headers=headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找所有卡片
            cards = soup.find_all('div', class_='card shadow-sm mt-3')
            page_results = []

            for card in cards:
                # 1. 提取标题 h5.card-title，替换 | 为 -
                title_tag = card.find('h5', class_='card-title')
                title = title_tag.get_text(strip=True) if title_tag else 'N/A'
                title = title.replace("|", "-")

                # 2. 提取流派：a 标签，class="badge badge-secondary"，带 href
                genre_tag = card.find('a', class_='badge badge-secondary', href=True)
                genre = genre_tag.get_text(strip=True) if genre_tag else 'N/A'

                # 3. 提取播放链接：a.btn-primary，包含文本 Play
                play_button = card.find('a', class_='btn btn-sm btn-primary', string=lambda t: t and 'Play' in t)
                stream_url = play_button['href'] if play_button and 'href' in play_button.attrs else 'N/A'

                # 如果 stream_url 是相对路径，拼接完整 URL
                if stream_url != 'N/A' and not stream_url.startswith('http'):
                    stream_url = urljoin(current_url, stream_url)

                # 拼接成一条记录
                # 这里sii中的格式为 "{stream_url}|{title}|{genre}|地区(全EN吧，毕竟全是外文歌)|码率(这要一个一个解析可且了咱就都写128完事)|0(我翻了一溜够也没看到对这个字段的说明，咱就照抄0吧)" 
                # 字段中如果是中文得转成utf8的16进制格式，但由于这次咱们从网页扒下来的全是英文也不用转了
                combined = f"{stream_url}|{title}|{genre}|EN|128|0"
                page_results.append(combined)

                # 用于去重检查（使用完整字符串作为唯一标识）
                if combined not in seen_items:
                    seen_items.add(combined)
                else:
                    print(f"⚠️ 发现重复条目: {combined}")

            # 保存本页结果
            all_results.extend(page_results)

            # 查找下一页按钮的链接
            next_button = soup.find('a', string=lambda t: t and 'Next' in t)
            if next_button and 'href' in next_button.attrs:
                next_page_url = next_button['href']
                current_url = urljoin(current_url, next_page_url)
            else:
                current_url = None  # 没有下一页了

            page_count += 1

        except Exception as e:
            print(f"抓取第 {page_count + 1} 页时出错: {e}")
            break

    # 去重统计
    total_items = len(all_results)
    unique_items = len(seen_items)
    has_duplicates = total_items != unique_items

    print("\n" + "="*50)
    print("抓取完成！")
    print(f"总共抓取条目数: {total_items}")
    print(f"去重后唯一条目数: {unique_items}")
    print(f"是否存在重复条目: {'是' if has_duplicates else '否'}")
    print("="*50)

    return list(seen_items), total_items  # 返回去重后的结果列表

# ======================
# 使用示例
# ======================

if __name__ == "__main__":
    # 当前示例使用一个假设的 URL，您需要替换为真实页面！
    target_url = "https://dir.xiph.org/codecs/MP3"  
    # 最多取6页，取更多也没啥意义，太多了也听不过来而且列表太长欧卡2会读不出来列表
    final_results,total_items  = scrape_multiple_pages(target_url, max_pages=6)


entries = []
for idx, item in enumerate(final_results, 0):
     entries.append(f'    stream_data[{idx}]: "{item}"')
    

# ✅ 拼接 SiiNunit 格式内容
sii_content = f"""SiiNunit
{{
  live_stream_def : _nameless.241.422c.1f60 {{
    stream_data: {total_items}
{chr(10).join(entries)}
  }}
}}
"""

# ✅ 打印结果（调试用，可选）
print(sii_content)

tmp_filename = "live_streams.sii.tmp"
try:
    with open(tmp_filename, 'w', encoding='utf-8') as f:
        f.write(sii_content)
    print(f"✅ 已写入临时文件: {tmp_filename}")
except Exception as e:
    print(f"⚠️ 写入临时文件失败: {e}")

# 备份旧的 live_streams.sii（如果有）
original_file = "live_streams.sii"
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"live_streams.sii.{timestamp}"

if os.path.exists(original_file):
    try:
        os.rename(original_file, backup_file)
        print(f"✅ 已备份原文件为: {backup_file}")
    except Exception as e:
        print(f"⚠️ 备份原文件失败: {e}")
else:
    print(f"ℹ️ 原文件 {original_file} 不存在，无需备份")

# 将临时文件重命名为正式文件
tmp_file = "live_streams.sii.tmp"
try:
    os.rename(tmp_file, original_file)
    print(f"✅ 已更新正式文件: {original_file}")
except Exception as e:
    print(f"⚠️ 重命名临时文件失败: {e}")