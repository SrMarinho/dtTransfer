from factories.queryable_factory import QueryableFactory


def main():
    v = QueryableFactory.getInstance('venda') 
    print(v.transferConfig()['from'])

if __name__ == "__main__":
    main()
