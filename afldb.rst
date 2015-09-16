.. function:: adddim    
    
    Produces a result array with one more dimension than the source array.
    
    ::
            
        adddim( srcArray, newDimName )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - newDimName: the name of a new dimension.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - adddim(A, loc) <quantity: uint64, sales: double> [loc, year,
          item] =
           loc, year, item, quantity, sales
           0, 2011, 2, 7, 31.64
           0, 2011, 3, 6, 19.98
           0, 2012, 1, 5, 41.65
           0, 2012, 2, 9, 40.68
           0, 2012, 3, 8, 26.64

.. function:: aggregate    
    
    Calculates aggregates over groups of values in an array, given the aggregate types and attributes to aggregate on.
    
    ::
            
        aggregate( srcArray {, AGGREGATE_CALL}+ {, groupbyDim}* )
            AGGREGATE_CALL := AGGREGATE_FUNC(inputAttr) [as resultName]
            AGGREGATE_FUNC := approxdc | avg | count | max | min | sum | stdev
           | var | some_use_defined_aggregate_function
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - 1 or more aggregate calls. Each aggregate call has an
          AGGREGATE_FUNC, an inputAttr and a resultName. The default
          resultName is inputAttr followed by '_' and then AGGREGATE_FUNC.
          For instance, the default resultName for sum(sales) is
          'sales_sum'. The count aggregate may take * as the input
          attribute, meaning to count all the items in the group including
          null items. The default resultName for count(*) is 'count'.
        - 0 or more dimensions that together determines the grouping
          criteria.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - aggregate(A, count(*), max(quantity), sum(sales), year) <count:
          uint64, quantity_max: uint64, sales_sum: double> [year] =
           year, count, quantity_max, sales_sum
           2011, 2, 7, 51.62
           2012, 3, 9, 108.97
    
    :notes:
        
        - All the aggregate functions ignore null values, except count(*).
    

.. function:: cumulate    
    
    Calculates a running aggregate over some aggregate along some fluxVector (a single dimension of the inputArray).
    
    ::
            
        cumulate ( inputArray {, AGGREGATE_ALL}+ [, aggrDim] )
            AGGREGATE_CALL := AGGREGATE_FUNC ( inputAttribute ) [ AS aliasName
           ]
            AGGREGATE_FUNC := approxdc | avg | count | max | min | sum | stdev
           | var | some_use_defined_aggregate_function
        
    
    :parameters:
        
           - inputArray: an input array
           - 1 or more aggregate calls.
           - aggrDim: the name of a dimension along with aggregates are computed.
             Default is the first dimension.
    
    
    :examples:
    
    ::
        
          input:         cumulate(input, sum(v) as sum_v, count(*) as cnt, I)
         +-I->
        J|     00   01   02   03       00       01       02       03
         V   +----+----+----+----+        +--------+--------+--------+--------+
         00  | 01 |    | 02 |    |   00   | (1, 1) |        | (3, 2) |        |
             +----+----+----+----+        +--------+--------+--------+--------+
         01  |    | 03 |    | 04 |   01   |        | (3, 1) |        | (7, 2) |
             +----+----+----+----+        +--------+--------+--------+--------+
         02  | 05 |    | 06 |    |   02   | (5, 1) |        | (11, 2)|        |
             +----+----+----+----+        +--------+--------+--------+--------+
         03  |    | 07 |    | 08 |   03   |        | (7, 1) |        | (15, 2)|
             +----+----+----+----+        +--------+--------+--------+--------+
    
    :notes:
        
        - For now, cumulate does NOT handle input array that have overlaps.
    

.. function:: regrid    
    
    Partitions the cells in the source array into blocks (with the given blockSize in each dimension), and for each block, calculates the required aggregates.
    
    ::
            
        regrid( srcArray {, blockSize}+ {, AGGREGATE_CALL}+ )
            AGGREGATE_CALL := AGGREGATE_FUNC(inputAttr) [as resultName]
            AGGREGATE_FUNC := approxdc | avg | count | max | min | sum | stdev
           | var | some_use_defined_aggregate_function
        
    
    :parameters:
        
        - srcArray: the source array with srcAttrs and srcDims.
        - A list of blockSizes, one for each dimension.
        - 1 or more aggregate calls. Each aggregate call has an
          AGGREGATE_FUNC, an inputAttr and a resultName. The default
          resultName is inputAttr followed by '_' and then AGGREGATE_FUNC.
          For instance, the default resultName for sum(sales) is
          'sales_sum'. The count aggregate may take * as the input
          attribute, meaning to count all the items in the group including
          null items. The default resultName for count(*) is 'count'.
    
    
    :notes:
        
        - Regrid does not allow a block to span chunks. So for every
          dimension, the chunk interval needs to be a multiple of the block
          size.
    

.. function:: window    
    
    Produces a result array with the same size and dimensions as the source array, where each ouput cell stores some aggregate calculated over a window around the corresponding cell in the source array. A pair of window specification values (leftEdge, rightEdge) must exist for every dimension in the source and output array.
    
    ::
            
        window( srcArray {, leftEdge, rightEdge}+ {, AGGREGATE_CALL}+ [,
           METHOD ] )
            AGGREGATE_CALL := AGGREGATE_FUNC(inputAttr) [as resultName]
            AGGREGATE_FUNC := approxdc | avg | count | max | min | sum | stdev
           | var | some_use_defined_aggregate_function
            METHOD := 'materialize' | 'probe'
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - leftEdge: how many cells to the left of the current cell (in one
          dimension) are included in the window.
        - rightEdge: how many cells to the right of the current cell (in
          one dimension) are included in the window.
        - 1 or more aggregate calls. Each aggregate call has an
          AGGREGATE_FUNC, an inputAttr and a resultName. The default
          resultName is inputAttr followed by '_' and then AGGREGATE_FUNC.
          For instance, the default resultName for sum(sales) is
          'sales_sum'. The count aggregate may take * as the input
          attribute, meaning to count all the items in the group including
          null items. The default resultName for count(*) is 'count'.
        - An optional final argument that specifies how the operator is to
          perform its calculation. At the moment, we support two internal
          algorithms: 'materialize' (which materializes an entire source
          chunk before computing the output windows) and 'probe' (which
          probes the source array for the data in each window). In general,
          materializing the input is a more efficient strategy, but when
          we're using thin(...) in conjunction with window(...), we're
          often better off using probes, rather than materilization. This
          is a decision that the optimizer needs to make.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - window(A, 0, 0, 1, 0, sum(quantity)) <quantity_sum: uint64>
          [year, item] =
           year, item, quantity_sum
           2011, 2, 7
           2011, 3, 13
           2012, 1, 5
           2012, 2, 14
           2012, 3, 17

.. function:: allversions    
    
    Creates a single array containing all versions of an existing array.
    
    ::
            
        allversions( srcArray )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - allversions(A) <quantity: uint64, sales:double> [VersionNo, year,
          item] =
           VersionNo, year, item, quantity, sales
           1, 2011, 2, 7, 31.64
           1, 2011, 3, 6, 19.98
           1, 2012, 1, 5, 41.65
           1, 2012, 2, 9, 40.68
           1, 2012, 3, 8, 26.64

.. function:: analyze    
    
    Returns an array describing the following characteristics of the specified attributes (or all the attributes, if no attribute is specified):

    * attribute_name
    * min
    * max
    * distinct_count: approximate count of distinct values.
    * non_null_count: the number of cells with non-null values.
    
    ::
            
        analyze( srcArray {, attr}* )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - 0 or more attributes.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - analyze(A) <attribute_name:string, min:string, max:string,
          distinct_count:uint64, non_null_count:uint64> [attribute_number]
          =
           attribute_number, attribute_name, min, max, distinct_count,
          non_null_count
           0, 'quantity' '5' '9' 5, 5
           1, 'sales' '19.98' '41.65' 5, 5
    
    :notes:
        
        - If multiple attributes are specified, the ordering of the
          attributes in the result array is determined by the ordering of
          the attributes in srcAttrs.
        - The value of attribute_number may be different from the number of
          an attribute in srcAttrs.
    

.. function:: apply    
    
    Produces a result array with new attributes and computes values for them.
    
    ::
            
        apply(srcArray {, newAttr, expression}+)
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - 1 or more pairs of a new attribute and the expression to compute
          the values for the attribute.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - apply(A, unitprice, sales/quantity) <quantity: uint64, sales:
          double, unitprice: double> [year, item] =
           year, item, quantity, sales, unitprice
           2011, 2, 7, 31.64, 4.52
           2011, 3, 6, 19.98, 3.33
           2012, 1, 5, 41.65, 8.33
           2012, 2, 9, 40.68, 4.52
           2012, 3, 8, 26.64, 3.33

.. function:: attribute_rename    
    
    Produces a result array the same as srcArray, but with at least one attribute renamed.
    
    ::
            
        attribute_rename( srcArray {, srcAttr, newAttr}+ )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - 1 or more pairs of a source attribute and the new attribute to
          rename to.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - attribute_rename(A, sales, totalsales) <quantity: uint64,
          totalsales:double> [year, item] =
           year, item, quantity, totalsales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64

.. function:: attributes    
    
    Produces a 1D result array where each cell describes one attribute of the source array.
    
    ::
            
        attributes( srcArray )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - attributes(A) <name:string, type_id:string, nullable:bool> [No] =
           No, name, type_id, nullable
           0, 'quantity', 'uint64', false
           1, 'sales', 'double', false

.. function:: bernoulli    
    
    Evaluates whether to include a cell in the result array by generating a random number and checks if it is less than probability.
    
    ::
            
        bernoulli( srcArray, probability [, seed] )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - probability: the probability threshold, in [0..1]
        - an optional seed for the random number generator.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - bernoulli(A, 0.5, 100) <quantity: uint64, sales:double> [year,
          item] =
           year, item, quantity, sales
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 3, 8, 26.64

.. function:: between    
    
    Produces a result array from a specified, contiguous region of a source array.
    
    ::
            
        between( srcArray {, lowCoord}+ {, highCoord}+ )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - the low coordinates
        - the high coordinates
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - between(A, 2011, 1, 2012, 2) <quantity: uint64, sales:double>
          [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
    
    :notes:
        
        - Almost the same as subarray. The only difference is that the
          dimensions retain the original start/end/boundaries.
    

.. function:: build    
    
    Produces a result array according to a given schema, and populates values based on the given expression. The schema must have a single attribute.
    
    ::
            
        build( schemaArray | schema, expression, mustBeConstant = false )
        
    
    :parameters:
        
        - schemaArray | schema: an array or a schema, from which attrs and
          dims will be used by the output array.
        - expression: the expression which is used to compute values for
          the output array.
        - mustBeConstant: whether the expression must be a constant.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64> [year, item] =
           year, item, quantity
           2011, 2, 7
           2011, 3, 6
           2012, 1, 5
           2012, 2, 9
           2012, 3, 8
        - build(A, 0) <quantity: uint64> [year, item] =
           year, item, quantity
           2011, 1, 0
           2011, 2, 0
           2011, 3, 0
           2012, 1, 0
           2012, 2, 0
           2012, 3, 0 Note that the cell (2011, 1), which was empty in the
          source array, is populated.
    
    :notes:
        
        - The build operator can only take as input bounded dimensions.
    

.. function:: cancel    
    
    Cancels a query by ID.
    
    ::
            
        cancel( queryId )
        
    
    :parameters:
        
        - queryId: the query ID that can be obtained from the SciDB log or
          via the list() command.
    
    
    :notes:
        
        - This operator is designed for internal use.
    

.. function:: cast    
    
    Produces a result array with data from srcArray but with the provided schema. There are three primary purposes:

    * To change names of attributes or dimensions.
    * To change types of attributes
    * To change a non-integer dimension to an integer dimension.
    * To change a nulls-disallowed attribute to a nulls-allowed attribute.
    
    ::
            
        cast( srcArray, schemaArray | schema )
        
    
    :parameters:
        
        - srcArray: a source array.
        - schemaArray | schema: an array or a schema, from which attrs and
          dims will be used by the output array.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - cast(A, <q:uint64, s:double>[y=2011:2012,2,0, i=1:3,3,0])
          <q:uint64, s:double> [y, i] =
           y, i, q, s
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64

.. function:: concat    
    
    Produces a result array as the concatenation of two source arrays. The concatenation is performed by the first dimension.
    
    ::
            
        concat( srcArray1, srcArray2 )
        
    
    :parameters:
        
        - srcArray1: the first source array with srcAttrs and srcDims1.
        - srcArray2: the second source array with srcAttrs and srcDim2,
          where srcDim2 may differ from srcDims1 only in the start/end of
          the first dimension.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - concat(A, A) <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
           2013, 2, 7, 31.64
           2013, 3, 6, 19.98
           2014, 1, 5, 41.65
           2014, 2, 9, 40.68
           2014, 3, 8, 26.64

.. function:: consume    
    
    Accesses each cell of an input array, if possible, by extracting tiles and iterating over tiles. numAttrsToScanAtOnce determines the number of attributes to scan as a group. Setting this value to '1' will result in a 'vertical' scan---all chunks of the current attribute will be scanned before moving on to the next attribute. Setting this value to the number of attributes will result in a 'horizontal' scan---chunk i of every attribute will be scanned before moving on to chunk i+1
    
    ::
            
        consume( array [, numAttrsToScanAtOnce] )
        
    
    :parameters:
        
        - array: the array to consume
        - numAttrsToScanAtOnce: optional 'stride' of the scan, default is 1
           Output array (an empty array):
        <
         >
         [
         ]
    

.. function:: create_array    
    
    Creates an array with the given name and schema and adds it to the database.
    
    ::
            
        *      create_array ( array_name, array_schema )
       *

        or

       *      CREATE ARRAY   array_name  array_schema
       *
        
    
    :parameters:
        
        - array_name: an identifier that names the new array.
        - array_schema: a multidimensional array schema that describes the
          rank and shape of the array to be created, as well as the types
          of each its attributes.
    

.. function:: cross_join    
    
    Calculates the cross product of two arrays, with 0 or more equality conditions on the dimensions. Assume p pairs of equality conditions exist. The result is an (m+n-p) dimensional array. From the coordinates of each cell in the result array, a single cell in leftArray and a single cell in rightArray can be located. The cell in the result array contains the concatenation of the attributes from the two source cells. If a pair of join dimensions have different lengths, the result array uses the smaller of the two.
    
    ::
            
        cross_join( leftArray, rightArray {, attrLeft, attrRight}* )
        
    
    :parameters:
        
        - leftArray: the left-side source array with leftAttrs and
          leftDims.
        - rightArray: the right-side source array with rightAttrs and
          rightDims.
        - 0 or more pairs of an attribute from leftArray and an attribute
          from rightArray.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - Given array B <v:uint64> [k] =
           k, v
           1, 10
           2, 20
           3, 30
           4, 40
           5, 50
        - cross_join(A, B, item, k) <quantity: uint64, sales:double,
          v:uint64> [year, item] =
           year, item, quantity, sales, v
           2011, 2, 7, 31.64, 20
           2011, 3, 6, 19.98, 30
           2012, 1, 5, 41.65, 10
           2012, 2, 9, 40.68, 20
           2012, 3, 8, 26.64, 30
    
    :notes:
        
        - Joining non-integer dimensions does not work.
    

.. function:: deldim    
    
    Produces a result array with one fewer dimension than the source array, by deleting the first dimension which must have size 1.
    
    ::
            
        deldim( srcArray )
        
    
    :parameters:
        
        - srcArray: a source array with dim1, dim2, ..., dim_kThe first
          dimension must have size 1.
    

.. function:: dimensions    
    
    List the dimensions of the source array.
    
    ::
            
        dimensions( srcArray )
        
    
    :parameters:
        
        - srcArray: a source array.
    

.. function:: diskinfo    
    
    Checks disk usage.
    
    ::
            
        diskinfo()
        
    
    :notes:
        
        - For internal usage.
    

.. function:: echo    
    
    Produces a single-element array containing the input string.
    
    ::
            
        echo( str )
        
    
    :parameters:
        
        - str: an input string.
    
    
    :notes:
        
        - For internal usage.
    

.. function:: explain_logical    
    
    Produces a single-element array containing the logical query plan.
    
    ::
            
        explain_logical( query , language = 'aql' )
        
    
    :parameters:
        
        - query: a query string.
        - language: the language string; either 'aql' or 'afl'; default is
          'aql'
    
    
    :notes:
        
        - For internal usage.
    

.. function:: explain_physical    
    
    Produces a single-element array containing the physical query plan.
    
    ::
            
        explain_physical( query , language = 'aql' )
        
    
    :parameters:
        
        - query: a query string.
        - language: the language string; either 'aql' or 'afl'; default is
          'aql'
    
    
    :notes:
        
        - For internal usage.
    

.. function:: filter    
    
    Produces a result array by filtering out (mark as empty) the cells in the source array for which the expression evaluates to False.
    
    ::
            
        filter( srcArray, expression )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - expression: an expression which takes a cell in the source array
          as input and evaluates to either True or False.
    

.. function:: help    
    
    Produces a single-element array containing the help information for an operator.
    
    ::
            
        help( operator )
        
    
    :parameters:
        
        - operator: the name of an operator.
    

.. function:: index_lookup    
    
    The input_array may have any attributes or dimensions. The index_array must have a single dimension and a single non-nullable attribute. The index array data must be sorted, unique values with no empty cells between them (though it does not necessarily need to be populated to the upper bound). The third argument must correctly refer to one of the attributes of the input array - the looked-up attribute. This attribute must have the same datatype as the only attribute of the index array. The comparison '<' function must be registered in SciDB for this datatype.
 The operator will create a new attribute, named input_attribute_name_index by default, or using the provided name, which will be the new last non-empty-tag attribute in the output array. The output attribute will be of type int64 nullable and will contain the respective coordinate of the corresponding input_attribute in index_array. If the corresponding input_attribute is null, or if no value for input_attribute exists in the index_array, the output attribute at that position shall be set to null. The output attribute shall be returned along all the input attributes in a fashion similar to the apply() operator.
 The operator uses some memory to cache a part of the index_array for fast lookup of values. By default, the size of this cache is limited to MEM_ARRAY_THRESHOLD. Note this is in addition to the memory already consumed by cached MemArrays as the operator is running. If a larger or smaller limit is desired, the 'memory_limit' parameter may be used. It is provided in units of mebibytes and must be at least 1.
 The operator may be further optimized to reduce memory footprint, optimized with a more clever data distribution pattern and/or extended to use multiple index arrays at the same time.
    
    ::
            
        index_lookup (input_array, index_array,
       input_array.attribute_name [,output_attribute_name]
       [,'memory_limit=MEMORY_LIMIT'])
        
    
    :parameters:
        
         input_array <..., input_attribute: type,... > [*]
         index_array <index_attribute: type not null>
        [dimension=0:any,any,any]
         input_attribute --the name of the input attribute
         [output_attribute_name] --the name for the output attribute if
        desired
         ['memory_limit=MEMORY_LIMIT'] --the memory limit to use MB)
    
    
    :examples:
    
    ::
        
         index_lookup(stock_trades, stock_symbols, stock_trades.ticker)
         index_lookup(stock_trades, stock_symbols, stock_trades.ticker,
        ticker_id, 'memory_limit=1024')

.. function:: input    
    
    Produces a result array and loads data from a given file, and optionally stores to shadowArray.
    
    ::
            
        input( schemaArray | schema, filename, instance=-2, format='',
           maxErrors=0, shadowArray='' )
        
    
    :parameters:
        
        - schemaArray | schema: the array schema.
        - filename: where to load data from.
        - instance: which instance; default is -2. ??
        - format: ??
        - maxErrors: ??
        - shadowArray: if provided, the result array will be written to it.
    
    
    :notes:
        
        - [comment from author] Must be called as
          INPUT('existing_array_name', '/path/to/file/on/instance'). ??
          schema not allowed??
        - This really needs to be modified by the author.
    

.. function:: insert    
    
    Inserts all data from left array into the persistent targetArray. targetArray must exist with matching dimensions and attributes. targetArray must also be mutable. The operator shall create a new version of targetArray that contains all data of the array that would have been received by merge(sourceArray, targetArrayName). In other words, new data is inserted between old data and overwrites any overlapping old values. The resulting array is then returned.
    
    ::
            
        insert( sourceArray, targetArrayName )
        
    
    :parameters:
        
        - sourceArray the array or query that provides inserted data
        - targetArrayName: the name of the persistent array inserted into
    
    
    :notes:
        
        Some might wonder - if this returns the same result as
        merge(sourceArray, targetArrayName), then why not use
        store(merge())? The answer is that
        1.  this runs a lot faster - it does not perform a full scan of
            targetArray
        2.  this also generates less chunk headers
    

.. function:: join    
    
    Combines the attributes of two arrays at matching dimension values. The two arrays must have the same dimension start coordinates, the same chunk size, and the same chunk overlap. The join result has the same dimension names as the first input. The cell in the result array contains the concatenation of the attributes from the two source cells. If a pair of join dimensions have different lengths, the result array uses the smaller of the two.
    
    ::
            
        join( leftArray, rightArray )
        
    
    :parameters:
        
        - leftArray: the left-side source array with leftAttrs and
          leftDims.
        - rightArray: the right-side source array with rightAttrs and
          rightDims.
    
    
    :notes:
        
        - join() is a special case of cross_join() with all pairs of
          dimensions given.
    

.. function:: list    
    
    Produces a result array and loads data from a given file, and optionally stores to shadowArray. The available things to list include:

    * aggregates: show all the aggregate operators.
    * arrays: show all the arrays.
    * chunk descriptors: show all the chunk descriptors.
    * chunk map: show the chunk map.
    * functions: show all the functions.
    * instances: show all SciDB instances.
    * libraries: show all the libraries that are loaded in the current SciDB session.
    * operators: show all the operators and the libraries in which they reside.
    * types: show all the datatypes that SciDB supports.
    * queries: show all the active queries.
    
    ::
            
        list( what='arrays', showSystem=false )
        
    
    :parameters:
        
        - what: what to list.
        - showSystem: whether to show systems information.
    

.. function:: load    
    
    Loads data to an existing outputArray from a given file, and optionally stores to shadowArray.
    
    ::
            
        load( outputArray, filename, instanceId=-2, format='', maxErrors=0,
           shadowArray='' )
        
    
    :parameters:
        
        - outputArray: the output array to store data into.
        - filename: A path to file where to load data from.
        - instanceId: positive number means an instance ID on which file
          will be saved. -1 means to save file on every instance. -2 - on
          coordinator.
        - format: format in which file will be stored. Possible values are
          'store', 'lcsv+', 'lsparse', 'dcsv', 'opaque', '(<custom
          plugin>=''>)'
        - maxErrors: a maximum number of errors which can take place due
          loading. After that exception is raised.
        - shadowArray: if provided a name of array where error of reading
          will be specified. The schema of array is the same as output
          array but all attribute has string data type + attribute
          [row_offset: int64]. It contains an error or reading every
          attribute with related name and row_offset - a position in file
          where an error was detected.
    
    
    :notes:
        
        - Must be called as INPUT('existing_array_name',
          '/path/to/file/on/instance').
        - This really needs to be checked by the author.
    

.. function:: load_library    
    
    Loads a SciDB plugin.
    
    ::
            
        load_library( library )
        
    
    :parameters:
        
        - library: the name of the library to load.
    
    
    :notes:
        
        - A library may be unloaded using unload_library()
    

.. function:: lookup    
    
    Retrieves the elements from srcArray, using coordinates stored in coordArray.
    
    ::
            
        lookup( coordArray, srcArray )
        
    
    :parameters:
        
        - coordArray: coordDims will be used as the dims in the output
          array, coordAttrs define coordinates in srcArray.
        - srcArray: srcDims and srcAttrs.
    

.. function:: materialize    
    
    Produces a materialized version of an source array.
    
    ::
            
        materialize( srcArray, format )
        
    
    :parameters:
        
        - srcArray: the sourcce array with srcDims and srcAttrs.
        - format: uint32, the materialize format.
    

.. function:: merge    
    
    Combines elements from the input arrays the following way: for each cell in the two inputs, if the cell of leftArray is not empty, the attributes from that cell are selected and placed in the output array; otherwise, the attributes from the corresponding cell in rightArray are taken. The two arrays should have the same attribute list, number of dimensions, and dimension start index. If the dimensions are not the same size, the output array uses the larger of the two.
    
    ::
            
        merge( leftArray, rightArray )
        
    
    :parameters:
        
        - leftArray: the left-hand-side array.
        - rightArray: the right-hand-side array.
    

.. function:: mstat    
    
    Gathers mallinfo from all the instances.
    
    ::
            
        mstat()
        

.. function:: normalize    
    
    Produces a result array by dividing each element of a 1-attribute vector by the square root of the sum of squares of the elements.
    
    ::
            
        normalize( srcArray )
        
    
    :parameters:
        
        - srcArray: the source array with srcAttrs and srcDims. There
          should be exactly one attribute (of double type) and exactly one
          dimension.
    

.. function:: project    
    
    Produces a result array that includes some attributes of the source array.
    
    ::
            
        project( srcArray {, selectedAttr}+ )
        
    
    :parameters:
        
        - srcArray: the source array with srcAttrs and srcDims.
        - a list of at least one selectedAttrs from the source array.
    

.. function:: avg_rank    
    
    Ranks the array elements, where each element is ranked as the average of the upper bound (UB) and lower bound (LB) rankings. The LB ranking of an element E is the number of elements less than E, plus 1. The UB ranking of an element E is the number of elements less than or equal to E, plus 1.
    
    ::
            
        avg_rank( srcArray [, attr {, groupbyDim}*] )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - 0 or 1 attribute to rank with. If no attribute is provided, the
          first attribute is used.
        - an optional list of groupbyDims used to group the elements, such
          that the rankings are calculated within each group. If no
          groupbyDim is provided, the whole array is treated as one group.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - avg_rank(A, sales, year) <sales:double, sales_rank: uint64>
          [year, item] =
           year, item, sales, sales_rank
           2011, 2, 31.64, 2
           2011, 3, 19.98, 1
           2012, 1, 41.65, 3
           2012, 2, 40.68, 2
           2012, 3, 26.64, 1
    
    :notes:
        
        - For any element with a distinct value, its UB ranking and LB
          ranking are equal.
    

.. function:: quantile    
    
    Computes the quantiles of an array, based on the ordering of attr (within each group as specified by groupbyDim, if specified). If groupbyDim is not specified, global ordering will be performed. If attr is not specified, the first attribute will be used.
    
    ::
            
        quantile( srcArray, numQuantiles [, attr {, groupbyDim}*] )
        
    
    :parameters:
        
        - srcArray: the source array with srcAttrs and srcDims.
        - numQuantiles: the number of quantiles.
        - attr: which attribute to sort on. The default is the first
          attribute.
        - groupbyDim: if provided, the ordering will be performed among the
          records in the same group.
    

.. function:: rank    
    
    Computes the rankings of an array, based on the ordering of attr (within each group as specified by the list of groupbyDims, if provided). If groupbyDims is not specified, global ordering will be performed. If attr is not specified, the first attribute will be used.
    
    ::
            
        rank( srcArray [, attr {, groupbyDim}*] )
        
    
    :parameters:
        
        - srcArray: the source array with srcAttrs and srcDims.
        - attr: which attribute to sort on. The default is the first
          attribute.
        - groupbyDim: if provided, the ordering will be performed among the
          records in the same group.
    

.. function:: redimension    
    
    Produces a array using some or all of the variables of a source array, potentially changing some or all of those variables from dimensions to attributes or vice versa, and optionally calculating aggregates to be included in the new array.
    
    ::
            
        redimension( srcArray, schemaArray | schema {, AGGREGATE_CALL}* )
            AGGREGATE_CALL := AGGREGATE_FUNC(inputAttr) [as resultName]
            AGGREGATE_FUNC := approxdc | avg | count | max | min | sum | stdev
           | var | some_use_defined_aggregate_function
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - schemaArray | schema: an array or schema from which outputAttrs
          and outputDims can be acquired. All the dimensions in outputDims
          must exist either in srcAttrs or in srcDims, with one exception.
          One new dimension called the synthetic dimension is allowed. All
          the attributes in outputAttrs, which is not the result of an
          aggregate, must exist either in srcAttrs or in srcDims.
        - 0 or more aggregate calls. Each aggregate call has an
          AGGREGATE_FUNC, an inputAttr and a resultName. The default
          resultName is inputAttr followed by '_' and then AGGREGATE_FUNC.
          The resultNames must already exist in outputAttrs.
    
    
    :notes:
        
        - The synthetic dimension cannot co-exist with aggregates. That is,
          if there exists at least one aggregate call, the synthetic
          dimension must not exist.
        - When multiple values are 'redimensioned' into the same cell in
          the output array, the collision handling depends on the schema:
          (a) If there exists a synthetic dimension, all the values are
          retained in a vector along the synthetic dimension. (b)
          Otherwise, for an aggregate attribute, the aggregate result of
          the values is stored. (c) Otherwise, an arbitrary value is picked
          and the rest are discarded.
        - Current redimension() does not support Non-integer dimensions or
          data larger than memory.
    

.. function:: reduce_distro    
    
    Makes a replicated array appear as if it has the required partitioningSchema.
    
    ::
            
        reduce_distro( replicatedArray, partitioningSchema )
        
    
    :parameters:
        
        - replicatedArray: an source array which is replicated across all
          the instances.
        - partitioningSchema: the desired partitioning schema.
    

.. function:: remove    
    
    Drops an array.
    
    ::
            
        remove( arrayToRemove )
        
    
    :parameters:
        
        - arrayToRemove: the array to drop.
    

.. function:: remove_versions    
    
    Removes all versions of targetArray that are older than oldestVersionToSave
    
    ::
            
        remove_versions( targetArray, oldestVersionToSave )
        
    
    :parameters:
        
        - targetArray: the array which is targeted.
        - oldestVersionToSave: the version, prior to which all versions
          will be removed.
    

.. function:: rename    
    
    Changes the name of an array.
    
    ::
            
        rename( oldArray, newArray )
        
    
    :parameters:
        
        - oldArray: an existing array.
        - newArray: the new name of the array.
    

.. function:: repart    
    
    Produces a result array similar to the source array, but with different chunk sizes, different chunk overlaps, or both.
    
    ::
            
        repart( srcArray, schema )
        
    
    :parameters:
        
        - srcArray: the source array with srcAttrs and srcDims.
        - schema: the desired schema.
    

.. function:: reshape    
    
    Produces a result array containing the same cells as, but a different shape from, the source array.
    
    ::
            
        reshape( srcArray, schema )
        
    
    :parameters:
        
        - srcArray: the source array with srcAttrs and srcDims.
        - schema: the desired schema, with the same attributes as srcAttrs,
          but with different size and/or number of dimensions. The
          restriction is that the product of the dimension sizes is equal
          to the number of cells in srcArray.
    

.. function:: reverse    
    
    Produces a result array, where the values of every dimension is reversed.
    
    ::
            
        reverse( srcArray )
        
    
    :parameters:
        
        - srcArray: the source array with srcAttrs and srcDims.
    

.. function:: save    
    
    Saves the data in an array to a file.
    
    ::
            
        save( srcArray, file, instanceId = -2, format = 'store' )
        
    
    :parameters:
        
        - srcArray: the source array to save from.
        - file: the file to save to.
        - instanceId: positive number means an instance ID on which file
          will be saved. -1 means to save file on every instance. -2 - on
          coordinator.
        - format: ArrayWriter format in which file will be stored
    
    
    :notes:
        
        n/a Must be called as SAVE('existing_array_name',
        '/path/to/file/on/instance')
    

.. function:: scan    
    
    Produces a result array that is equivalent to a stored array.
    
    ::
            
        scan( srcArray )
        
    
    :parameters:
        
        - srcArray: the array to scan, with srcAttrs and srcDims
    

.. function:: setopt    
    
    Gets/Sets a config option at runtime.
    
    ::
            
        setopt( option [, newValue] )
        
    
    :parameters:
        
        - option: the config option.
        - newValue: an optional new value for the config option. If
          provided, the option is set. Either way, the option value(s) is
          returned.
    

.. function:: sg    
    
    SCATTER/GATHER distributes array chunks over the instances of a cluster. The result array is returned. It is the only operator that uses the network manager. Typically this operator is inserted by the optimizer into the physical plan.
    
    ::
            
        sg( srcArray, partitionSchema, instanceId=-1, outputArray='',
           isStore=true, offsetVector=null)
        
    
    :parameters:
        
        - srcArray: the source array, with srcAttrs and srcDims.
        - partitionSchema:
           0 = psReplication,
           1 = psHashPartitioned,
           2 = psLocalInstance,
           3 = psByRow,
           4 = psByCol,
           5 = psUndefined.
        - instanceId:
           -2 = to coordinator (same with 0),
           -1 = all instances participate,
           0..#instances-1 = to a particular instance.
           [TO-DO: The usage of instanceId, in calculating which instance a
          chunk should go to, requires further documentation.]
        - outputArray: if not empty, the result will be stored into this
          array
        - isStore: whether to store into the specified outputArray.
           [TO-DO: Donghui believes this parameter is not needed and should
          be removed.]
        - offsetVector: a vector of #dimensions values.
           To calculate which instance a chunk belongs, the chunkPos is
          augmented with the offset vector before calculation.
    

.. function:: show    
    
    Shows the schema of an array.
    
    ::
            
        show( schemaArray | schema | queryString [, 'aql' | 'afl'] )
        
    
    :parameters:
        
        - schemaArray | schema | queryString: an array where the schema is
          used, the schema itself or arbitrary query string
        o
    

.. function:: slice    
    
    Produces a 'slice' of the source array, by holding zero or more dimension values constant. The result array does not include the dimensions that are used for slicing.
    
    ::
            
        slice( srcArray {, dim, dimValue}* )
        
    
    :parameters:
        
        - srcArray: the source array with srcAttrs and srcDims.
        - dim: one of the dimensions to be used for slicing.
        - dimValue: the constant value in the dimension to slice.
    

.. function:: sort    
    
    Produces a 1D array by sorting the non-empty cells of a source array.
    
    ::
            
        sort( srcArray {, attr [asc | desc]}* {, chunkSize}? )
        
    
    :parameters:
        
        - srcArray: the source array with srcAttrs and srcDim.
        - attr: the list of attributes to sort by. If no attribute is
          provided, the first attribute will be used.
        - asc | desc: whether ascending or descending order of the
          attribute should be used. The default is asc.
        - chunkSize: the size of a chunk in the result array. If not
          provided, 1M will be used.
    
    
    :notes:
        
        Assuming null < NaN < other values
    

.. function:: sort2    
    
    Produces a 1D array by sorting the non-empty cells of a source array.
    
    ::
            
        sort( srcArray {, attr [asc | desc]}* {, chunkSize}? )
        
    
    :parameters:
        
        - srcArray: the source array with srcAttrs and srcDim.
        - attr: the list of attributes to sort by. If no attribute is
          provided, the first attribute will be used.
        - asc | desc: whether ascending or descending order of the
          attribute should be used. The default is asc.
        - chunkSize: the size of a chunk in the result array. If not
          provided, 1M will be used.
    
    
    :notes:
        
        Assuming null < NaN < other values
    

.. function:: store    
    
    Stores an array to the database. Each execution of store() causes a new version of the array to be created.
    
    ::
            
        store( srcArray, outputArray )
        
    
    :parameters:
        
        - srcArray: the source array with srcAttrs and srcDim.
        - outputArray: an existing array in the database, with the same
          schema as srcArray.
    

.. function:: subarray    
    
    Produces a result array from a specified, contiguous region of a source array.
    
    ::
            
        subarray( srcArray {, lowCoord}+ {, highCoord}+ )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - the low coordinates
        - the high coordinates
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - subarray(A, 2011, 1, 2012, 2) <quantity: uint64, sales:double>
          [year, item] =
           year, item, quantity, sales
           0, 1, 7, 31.64
           1, 0, 5, 41.65
           1, 1, 9, 40.68
    
    :notes:
        
        - Almost the same as between(). The only difference is that the
          dimensions are 'cropped'.
    

.. function:: substitute    
    
    Produces a result array the same as srcArray, but with null values (of selected attributes) substituted using the values in substituteArray.
    
    ::
            
        substitute( srcArray, substituteArray {, attr}* )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims, that may
          contain null values.
        - substituteArray: the array from which the values may be used to
          substitute the null values in srcArray. It must have a single
          dimension which starts at 0, and a single attribute.
        - An optional list of attributes to substitute. The default is to
          substitute all nullable attributes.
    

.. function:: thin    
    
    Selects regularly-spaced elements of the source array in each dimension. A (start, step) pair must be provided for every dimension.
    
    ::
            
        thin( srcArray {, start, step}+ )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - start: the starting coordinate of a dimension.
        - step: how many coordinates to advance to the next coordinate to
          select. A step of 1 means to select everything.
    

.. function:: transpose    
    
    Produces an array with the same data in srcArray but with the list of dimensions reversd.
    
    ::
            
        transpose( srcArray )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
    

.. function:: unfold    
    
    Complicated input data are often loaded into table-like 1-d multi- attribute arrays. Sometimes we want to assemble uniformly-typed subsets of the array attributes into a matrix, for example to compute correlations or regressions. unfold will transform the input array into a 2-d matrix whose columns correspond to the input array attributes. The output matrix row dimension will have a chunk size equal to the input array, and column chunk size equal to the number of columns.
    
    ::
            
        unfold( array )
        
    
    :parameters:
        
        - array: the array to consume
    
    
    :examples:
    
    ::
        
        unfold(apply(build(<v:double>[i=0:9,3,0],i),w,i+0.5))

.. function:: uniq    
    
    The input array must have a single attribute of any type and a single dimension. The data in the input array must be sorted and dense. The operator is built to accept the output produced by sort() with a single attribute. The output array shall have the same attribute with the dimension i starting at 0 and chunk size of 1 million. An optional chunk_size parameter may be used to set a different output chunk size. Data is compared using a simple bitwise comparison of underlying memory. Null values are discarded from the output.
    
    ::
            
        uniq (input_array [,'chunk_size=CHUNK_SIZE'] )
        
    
    :parameters:
        
         array <single_attribute: INPUT_ATTRIBUTE_TYPE> [single_dimension=
        *]
    
    
    :examples:
    
    ::
        
         uniq (sorted_array)
         store ( uniq ( sort ( project (big_array, string_attribute) ),
        'chuk_size=100000'), string_attribute_index )

.. function:: unload_library    
    
    Unloads a SciDB plugin.
    
    ::
            
        unload_library( library )
        
    
    :parameters:
        
        - library: the name of the library to unload.
    
    
    :notes:
        
        - This operator is the reverse of load_library().
    

.. function:: old_unpack    
    
    Unpacks a multi-dimensional array into a single-dimensional array, creating new attributes to represent the dimensions in the source array.
    
    ::
            
        unpack( srcArray, newDim )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - newDim: the name of the dimension in the result 1D array.
    

.. function:: unpack    
    
    Unpacks a multi-dimensional array into a single-dimensional array, creating new attributes to represent the dimensions in the source array.
    
    ::
            
        unpack( srcArray, newDim )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - newDim: the name of the dimension in the result 1D array.
    

.. function:: variable_window    
    
    Produces a result array with the same dimensions as the source array, where each cell stores some aggregates calculated over a 1D window covering the current cell. The window has fixed number of non-empty elements. For instance, when rightEdge is 1, the window extends to the right-hand side however number of coordinatesthat are needed, to cover the next larger non-empty cell.
    
    ::
            
        variable_window( srcArray, dim, leftEdge, rightEdge {,
           AGGREGATE_CALL}+ )
            AGGREGATE_CALL := AGGREGATE_FUNC(inputAttr) [as resultName]
            AGGREGATE_FUNC := approxdc | avg | count | max | min | sum | stdev
           | var | some_use_defined_aggregate_function
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - dim: along which dimension is the window defined.
        - leftEdge: how many cells to the left of the current cell are
          included in the window.
        - rightEdge: how many cells to the right of the current cell are
          included in the window.
        - 1 or more aggregate calls. Each aggregate call has an
          AGGREGATE_FUNC, an inputAttr and a resultName. The default
          resultName is inputAttr followed by '_' and then AGGREGATE_FUNC.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - variable_window(A, item, 1, 0, sum(quantity)) <quantity_sum:
          uint64> [year, item] =
           year, item, quantity_sum
           2011, 2, 7
           2011, 3, 13
           2012, 1, 5
           2012, 2, 14
           2012, 3, 17
    
    :notes:
        
        - For a dense array, this is a special case of window().
        - For the aggregate function approxdc(), the attribute name is
          currently non-conventional. It is xxx_ApproxDC instead of
          xxx_approxdc. Should change.
    

.. function:: versions    
    
    Lists all versions of an array in the database.
    
    ::
            
        versions( srcArray )
        
    
    :parameters:
        
        - srcArray: a source array.
    

.. function:: xgrid    
    
    Produces a result array by 'scaling up' the source array. Within each dimension, the operator duplicates each cell a specified number of times before moving to the next cell. A scale must be provided for every dimension.
    
    ::
            
        xgrid( srcArray {, scale}+ )
        
    
    :parameters:
        
        - srcArray: a source array with srcAttrs and srcDims.
        - scale: for each dimension, a scale is provided telling how much
          larger the dimension should grow.
    
    
    :examples:
    
    ::
        
        - Given array A <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 2, 7, 31.64
           2011, 3, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 9, 40.68
           2012, 3, 8, 26.64
        - xgrid(A, 1, 2) <quantity: uint64, sales:double> [year, item] =
           year, item, quantity, sales
           2011, 3, 7, 31.64
           2011, 4, 7, 31.64
           2011, 5, 6, 19.98
           2011, 6, 6, 19.98
           2012, 1, 5, 41.65
           2012, 2, 5, 41.65
           2012, 3, 9, 40.68
           2012, 4, 9, 40.68
           2012, 5, 8, 26.64
           2012, 6, 8, 26.64