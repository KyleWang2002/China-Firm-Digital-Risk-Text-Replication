"""Opt-in low-rate CNINFO querying and retrieval; API response formats may change."""
import re
import time
from pathlib import Path
from urllib.parse import urlparse

BASE = 'https://www.cninfo.com.cn/new/hisAnnouncement/query'
PDF_HOST = 'static.cninfo.com.cn'


def crawl_announcements(start, end, pages=1, delay=3.0):
    if delay < 2.0:
        raise ValueError('Use at least 2 seconds between requests')
    try:
        import requests
    except ImportError as exc:
        raise RuntimeError('pip install -e ".[collect]"') from exc
    s=requests.Session()
    s.headers.update({'User-Agent':'AcademicResearchContact/1.0 (low-volume; CNINFO public filings)'})
    all_rows=[]
    for page in range(1, pages+1):
        response=s.post(BASE, timeout=30, data={
            'pageNum':page,'pageSize':30,'column':'szse','tabName':'fulltext',
            'plate':'sz;sh','category':'category_ndbg_szsh',
            'seDate':f'{start}~{end}','sortName':'code','sortType':'asc'})
        response.raise_for_status()
        body=response.json()
        if not isinstance(body.get('announcements'),list):
            raise RuntimeError('Unexpected CNINFO JSON; inspect endpoint and filters')
        for item in body['announcements']:
            link=item.get('adjunctUrl','').lstrip('/')
            if not link or '..' in link: continue
            title=re.sub('<[^>]+>', '', item.get('announcementTitle',''))
            all_rows.append({'firm_id':item.get('secCode',''),
                             'company':item.get('secName',''),
                             'title':title,
                             'publication_date':item.get('announcementTime',''),
                             'url':f'https://{PDF_HOST}/{link}',
                             'source':'CNINFO'})
        if page < pages:
            time.sleep(delay)
    return all_rows


def download_catalog(catalog, destination, limit=3, delay=3.0):
    from .io import read_rows, write_rows
    if delay < 2.0: raise ValueError('Use at least 2 seconds between requests')
    import requests
    destination=Path(destination); destination.mkdir(parents=True,exist_ok=True)
    results=[]
    for row in list(read_rows(catalog))[:limit]:
        link=row.get('url') or row.get('年报链接','')
        parsed=urlparse(link)
        if parsed.scheme != 'https' or parsed.hostname != PDF_HOST:
            results.append({'firm_id':row.get('firm_id', row.get('公司代码','')),
                            'status':'skipped_non_cninfo_https','filename':''})
            continue
        code=row.get('firm_id') or row.get('公司代码') or 'unknown'
        year=row.get('year') or row.get('年份') or 'unknown'
        if not re.fullmatch(r'[\w-]{1,30}',code+year):
            raise ValueError('Unsafe ID/year string in catalog')
        path=destination/f'{code}_{year}.pdf'
        try:
            res=requests.get(link,timeout=45,headers={'User-Agent':'AcademicResearchContact/1.0'},stream=True)
            res.raise_for_status()
            with path.open('wb') as fout:
                first=True
                for chunk in res.iter_content(chunk_size=32768):
                    if not chunk: continue
                    if first:
                        if not chunk.startswith(b'%PDF'):
                            raise ValueError('Response is not a PDF')
                        first=False
                    fout.write(chunk)
            status='downloaded'
        except Exception as exc:
            path.unlink(missing_ok=True)
            status=f'ERROR: {exc}'
        results.append({'firm_id':code,'status':status,'filename':path.name if path.exists() else ''})
        if len(results)<limit: time.sleep(delay)
    write_rows(destination/'download_audit.csv',results,['firm_id','status','filename'])
    return results
