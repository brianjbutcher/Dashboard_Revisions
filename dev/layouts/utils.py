import logging
import query as mongo_query

_logger = logging.getLogger(__name__)

__BLK_DB__ = 'BLK___{}___FBCStats'


def query_histogram(query, dbvalue, colvalue):
    # split into two functions

    query_result = mongo_query.run_query(dbvalue, colvalue, query)
    #print(query_result)
    for each in query_result:
        each['_id_pair'] = dict(zip(each['_id_name'].split(','), each['_id'].split(',')))
        #each['_id'] = each['_id_pair']

    return tuple(dict(
            value=tuple(zip(*sorted((int(x), int(y)) for x, y in record.items() if x not in ('_id', '_id_name', '_id_pair', '_id_type')))),
            _id_pair=record['_id_pair'])for record in query_result)


def query_statistic(query, dbvalue, colvalue):
    # split into two functions

    query_result = mongo_query.run_query(dbvalue, colvalue, query)
    #print(query_result)
    for each in query_result:
        each['_id_pair'] = dict(zip(each['_id_name'].split(','), each['_id'].split(',')))
        #each['_id'] = each['_id_pair']

    return query_result

__NUMBER_WORD_MAP__ = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']

def number_to_word(num):
    return __NUMBER_WORD_MAP__[num]

def statistic_upper_limit(dbvalue, colvalue, testtype, duttype =None, dietype = None):
    #dbvalue = __BLK_DB__.format(product_choice)
    query = {"$and": [{"_id": {"$regex": testtype}},]}
    if duttype: query["$and"].append({"_id": {"$regex": duttype}})
    if dietype: query["$and"].append({"_id": {"$regex": dietype}})
    #_logger.info(mongo_query.get_ranking(dbvalue, colvalue, query, 'max', 1)[0])
    return mongo_query.get_ranking(dbvalue, colvalue, query, 'max', 1)[0]['max']