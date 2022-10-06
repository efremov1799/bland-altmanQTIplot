import numpy


def ba_simple(t, var_var1, var_var2):
    #get the data corresponded to specified names
    var1=t.colData(var_var1)
    var2=t.colData(var_var2)

    #check and pop if data is numeric and contains no missing values:
    for i in range(0,len(var2)):
        if var1[i]==None or var2[i]==None:
            var1[i]=None; var2[i]=None
    var1=filter(lambda x: x!=None, var1)  
    var2=filter(lambda x: x!=None, var2)       

    # vectors of BA params calculation:
    diff=[(var1[i]-var2[i]) for i in range(0,len(var2))]
    dfsd=numpy.std(diff); dfav = numpy.mean(diff); dfnn = len(diff)
    bias=[dfav for i in range(0,dfnn)]   
    hasum=[(var1[i]+var2[i])/2 for i in range(0,dfnn)] 
    up2sigmas=[(dfav+2*dfsd) for i in range(0,dfnn)]
    down2sigmas=[(dfav-2*dfsd) for i in range(0,dfnn)]
    
    #icc calculation and interpretation 
    icc=1-dfsd*dfsd/(numpy.std(hasum)*numpy.std(hasum))
    iccOK="poor"
    if icc>0.5: iccOK="moderate"
    if icc>0.75: iccOK="good"
    if icc>0.9: iccOK="excellent"
   
    #outlier detection:
    outlierL=[(1+numpy.sign(diff[i]-down2sigmas[1]))/2 for i in range(0,dfnn)]
    outlierU=[(1+numpy.sign(diff[i]-up2sigmas[1]))/2 for i in range(0,dfnn)]
    outlier=[((abs(outlierU[i]+outlierL[i])-1)) for i in range(0,dfnn)] 
    outliertot=sum(numpy.abs(outlier))
    outlierTxt=["o" for i in range(0,dfnn)] 
    for i in range(0, dfnn):
        if outlier[i]!=0: 
            outlierTxt[i]="x"

    #CI95% for bias - check if bias is significant
    biasL=bias[1]-2*dfsd/numpy.sqrt(dfnn)
    biasU=bias[1]+2*dfsd/numpy.sqrt(dfnn)
    biasOK="significant (p<0.05)"
    if biasL<0 and biasU>0:
        biasOK="not significant (p>0.05)"

    #return set:
    ret=[0 for i in range(0,9)]
    ret[0]=dfnn
    ret[1]=bias[1]
    ret[2]=icc   
    ret[3]=outliertot
    ret[4]=biasOK
    ret[5]=iccOK

    #new table to place BA data     
    t_n=newTable("Bland-Altman",dfnn,6)
    #1stCol
    t_n.setColName(1,"HalfSum")
    t_n.setColData(1,hasum)
    #2ndCol
    t_n.setColName(2, "Diff")
    t_n.setColData(2, diff)
    t_n.setColumnWidth(2, 55)
    #3thCol
    t_n.setColName(3, "Bias")
    t_n.setColData(3, bias)
    t_n.setColumnWidth(3, 55)
    #4thCol
    t_n.setColName(4, "LowerAgreementLimit")
    t_n.setColData(4, down2sigmas)
    t_n.setColumnWidth(4, 55)
    #5thCol
    t_n.setColName(5, "UpperAgreementLimit")
    t_n.setColData(5, up2sigmas)
    t_n.setColumnWidth(5, 55)
    #6thCol
    t_n.setColName(6, "Outliers")
    t_n.setColTextFormat(6)
    t_n.setColData(6, outlierTxt)
    #t_n.setColData(6, outlier)
 
    return(ret)


#body:
t = currentTable()
try:
    tmp2=t.colName(t.selectedColumn()+1)
    tmp=t.colName(t.selectedColumn()) 
except Exception as x:
    tmp="colName1"
    tmp2="colName2"
user_string, isOK=QtGui.QInputDialog.getText(qti.app,
                                             "Bland-Altman",
                                             "Specify statement as 'Var1$vs$Var2':",
                                             QtGui.QLineEdit.Normal,
                                             str(tmp2)+"$vs$"+str(tmp))
if isOK:
    try:
        tmp=list(str(user_string))
        for i in range(0,len(tmp)-4):
            if (tmp[i]=='$' and tmp[i+1]=='v' and tmp[i+2]=='s' and tmp[i+3]=='$'):
                index_stop=i
        var_var2=''.join([tmp[i] for i in range(0,index_stop)])
        var_var1=''.join([tmp[i] for i in range(index_stop+4, len(tmp))])            
        del(tmp); del(tmp2) 
        ret=ba_simple(t, str(var_var1), str(var_var2))
    except Exception as x:
        QtGui.QMessageBox.warning(qti.app, 'Failed! Check statement syntax or data types...', x.__str__())
    

resultsLog().append("\n===== Bland-Altman analysis and ICC=======")
resultsLog().append("Test sample vs. reference sample: \n"+str(var_var2)+" vs. "+str(var_var1))
resultsLog().append("\n"+">>  Bias = "+str((ret[1])))
resultsLog().append(">>  Bias is "+ret[4])
resultsLog().append("\n"+">>  Intraclass Correlation Coef. = "+str(0.001*round(1000*(ret[2]))))
resultsLog().append(">>  Agreement is "+ret[5])
resultsLog().append("\n"+">>  "+str(int(ret[3]))+" outliers detected")
resultsLog().append("============\n")
