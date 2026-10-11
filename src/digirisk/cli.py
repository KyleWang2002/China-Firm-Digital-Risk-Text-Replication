"""Command-line entry points to the transparent replication scaffold."""
import argparse
from .io import write_rows


def main(argv=None):
    parser=argparse.ArgumentParser(prog='digirisk')
    sub=parser.add_subparsers(dest='step',required=True)
    s=sub.add_parser('crawl', help='opt-in limited CNINFO catalog query')
    s.add_argument('--start',required=True);s.add_argument('--end',required=True)
    s.add_argument('--pages',type=int,default=1);s.add_argument('--delay',type=float,default=3)
    s.add_argument('--out',required=True)
    s=sub.add_parser('download',help='opt-in limited official PDF download')
    s.add_argument('--catalog',required=True);s.add_argument('--out-dir',required=True)
    s.add_argument('--limit',type=int,default=3);s.add_argument('--delay',type=float,default=3)
    s=sub.add_parser('pdf-to-txt',help='convert locally available PDF files')
    s.add_argument('--input-dir',required=True);s.add_argument('--out-dir',required=True)
    s=sub.add_parser('extract-mda',help='extract MD&A, then manually inspect audit')
    s.add_argument('--input-dir',required=True);s.add_argument('--out-dir',required=True)
    s=sub.add_parser('match',help='select candidate sentences from MD&A')
    s.add_argument('--input-dir',required=True);s.add_argument('--lexicon',required=True)
    s.add_argument('--out',required=True);s.add_argument('--metadata')
    s=sub.add_parser('queue',help='make blank annotation review sheet')
    s.add_argument('--input',required=True);s.add_argument('--out',required=True)
    s=sub.add_parser('reconcile',help='validate two-model+human labels')
    s.add_argument('--input',required=True);s.add_argument('--out',required=True)
    s=sub.add_parser('index',help='construct firm-year exposure indices')
    s.add_argument('--input',required=True);s.add_argument('--out',required=True)
    s.add_argument('--universe-csv',help='Optional firm_id,year,mda_verified CSV for audited zero-fill')
    s=sub.add_parser('expand-word2vec',help='suggest unverified lexicon extensions')
    s.add_argument('--lexicon',required=True);s.add_argument('--vectors',required=True)
    s.add_argument('--out',required=True)
    args=parser.parse_args(argv)
    if args.step=='crawl':
        from .cninfo import crawl_announcements
        rows=crawl_announcements(args.start,args.end,args.pages,args.delay)
        write_rows(args.out,rows,['firm_id','company','title','publication_date','url','source'])
        print(f'Saved {len(rows)} catalog items; not vetted for duplicate/summary announcements')
    elif args.step=='download':
        from .cninfo import download_catalog
        print(f'Processed {len(download_catalog(args.catalog,args.out_dir,args.limit,args.delay))} links')
    elif args.step=='pdf-to-txt':
        from .pdf import batch_convert
        print(f'Processed {len(batch_convert(args.input_dir,args.out_dir))} PDFs; inspect conversion_audit.csv')
    elif args.step=='extract-mda':
        from .mda import batch_extract
        print(f'Processed {len(batch_extract(args.input_dir,args.out_dir))} TXT files; inspect extraction_audit.csv')
    elif args.step=='match':
        from .lexicon import batch_match
        print(f'Extracted {batch_match(args.input_dir,args.lexicon,args.out,args.metadata)} candidate sentences')
    elif args.step=='queue':
        from .annotation import annotation_queue
        print(f'Created {annotation_queue(args.input,args.out)} annotation rows')
    elif args.step=='reconcile':
        from .annotation import reconcile
        print(f'Review: {reconcile(args.input,args.out)} (rows, pending human review)')
    elif args.step=='index':
        from .score import aggregate
        print(f'Aggregated {aggregate(args.input,args.out,args.universe_csv)} firm-year observations')
    elif args.step=='expand-word2vec':
        from .embedding import propose_extensions
        print(f'Generated {propose_extensions(args.lexicon,args.vectors,args.out)} candidates awaiting human screening')

if __name__=='__main__':main()
