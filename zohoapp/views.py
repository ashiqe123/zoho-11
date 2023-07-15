from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import messages
from django.utils.text import capfirst
from django.contrib.auth.models import User,auth
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.views import View
from .forms import EmailForm
from django.http import JsonResponse
from datetime import datetime,date, timedelta
from xhtml2pdf import pisa
from django.template.loader import get_template
from bs4 import BeautifulSoup
import io
import os
import json
from django.template import Context, Template
import tempfile
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST


def index(request):

    return render(request,'index.html')

def register(request):
    if request.method=='POST':

        first_name=capfirst(request.POST['fname'])
        last_name=capfirst(request.POST['lname'])
        username=request.POST['uname']
        password=request.POST['password']
        cpassword=request.POST['cpassword']
        email=request.POST['email1']
        phone = request.POST['phone']

      
        if password==cpassword:  #  password matching......
            if User.objects.filter(username=username).exists(): #check Username Already Exists..
                messages.info(request, 'This username already exists!!!!!!')
                return redirect('register')
            else:
                user=User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    password=password,
                    email=email)
                
                user.save()
                u = User.objects.get(id = user.id)

                company_details(contact_number = phone, user = u).save()
        else:
            messages.info(request, 'Password doesnt match!!!!!!!')
            print("Password is not Matching.. ") 
            return redirect('register')   
        return redirect('register')

    return render(request,'register.html',{'msg' : messages})

def login(request):
        
    if request.method == 'POST':
        
        email_or_username = request.POST['emailorusername']
        password = request.POST['password']
        print(password)
        user = authenticate(request, username=email_or_username, password=password)
        print(user)
        if user is not None:
            auth.login(request, user)
            return redirect('base')
        else:
            return redirect('/')

    return render(request, 'register.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('/')

def forgotpassword(request):
     return render(request,'setpassword.html')

def setnewpassword(request):

    if request.method=='POST':
        email_or_username = request.POST['emailorusername']
        password=request.POST['password']
        cpassword=request.POST['cpassword']
        if password==cpassword:

            c = User.objects.filter(Q(username = email_or_username)|Q(email = email_or_username)).first()
            c.set_password(password)
            c.save()

        return redirect('register' )
        
    else:
        return render(request, 'setpassword.html')

@login_required(login_url='login')
def base(request):
   
       
    if not Unit.objects.filter(unit='BOX').exists():
            Unit(unit='BOX').save()
    if not Unit.objects.filter(unit='UNIT').exists():
            Unit(unit='UNIT').save()
    if not Unit.objects.filter(unit='LITRE').exists():
            Unit(unit='LITRE').save()

    if not Sales.objects.filter(Account_name='General Income').exists():
            Sales(Account_type='INCOME',Account_name='General Income',Account_desc='salesincome').save()
    if not Sales.objects.filter(Account_name='Intrest Income').exists():
            Sales(Account_type='INCOME',Account_name='Intrest Income',Account_desc='salesincome').save()
    if not Sales.objects.filter(Account_name='Late fee Income').exists():
            Sales(Account_type='INCOME',Account_name='Late fee Income',Account_desc='salesincome').save()
    if not Sales.objects.filter(Account_name='Discount Income').exists():
            Sales(Account_type='INCOME',Account_name='Discount Income',Account_desc='salesincome').save()
    if not Sales.objects.filter(Account_name='Other Charges').exists():
            Sales(Account_type='INCOME',Account_name='Other Charges',Account_desc='salesincome').save()
    if not Sales.objects.filter(Account_name='Shipping Charge').exists():
            Sales(Account_type='INCOME',Account_name='Shipping Charge',Account_desc='salesincome').save()


    if not  Purchase.objects.filter(Account_name='Advertising & Marketing').exists():
            Purchase(Account_type='EXPENCES',Account_name='Advertising & Markting',Account_desc='Advertsing Exp').save()
    if not Purchase.objects.filter(Account_name='Debit Charge').exists():
            Purchase(Account_type='EXPENCES',Account_name='Debit Charge',Account_desc='Debited Exp').save()
    if not Purchase.objects.filter(Account_name='Labour Charge').exists():
            Purchase(Account_type='EXPENCES',Account_name='Labour Charge',Account_desc='Labour Exp').save()
    if not Purchase.objects.filter(Account_name='Raw Meterials').exists():
            Purchase(Account_type='EXPENCES',Account_name='Raw Meterials',Account_desc='Raw Meterials Exp').save()

    company = company_details.objects.get(user = request.user)
    context = {
                'company' : company
            }
    return render(request,'loginhome.html',context)


@login_required(login_url='login')
def view_profile(request):

    company = company_details.objects.get(user = request.user)
    context = {
                'company' : company
            }
    return render(request,'profile.html',context)

@login_required(login_url='login')
def edit_profile(request,pk):

    company = company_details.objects.get(id = pk)
    user1 = User.objects.get(id = company.user_id)

    if request.method == "POST":

        user1.first_name = capfirst(request.POST.get('f_name'))
        user1.last_name  = capfirst(request.POST.get('l_name'))
        user1.email = request.POST.get('email')
        company.contact_number = request.POST.get('cnum')
        company.address = capfirst(request.POST.get('ards'))
        company.company_name = request.POST.get('comp_name')
        company.company_email = request.POST.get('comp_email')
        company.city = request.POST.get('city')
        company.state = request.POST.get('state')
        company.country = request.POST.get('country')
        company.pincode = request.POST.get('pinc')
        company.gst_num = request.POST.get('gst')
        company.pan_num = request.POST.get('pan')
        company.business_name = request.POST.get('bname')
        company.company_type = request.POST.get('comp_type')
        if len(request.FILES)!=0 :
            company.profile_pic = request.FILES.get('file')

        company.save()
        user1.save()
        return redirect('view_profile')

    context = {
        'company' : company,
        'user1' : user1,
    }
    
    return render(request,'edit_profile.html',context)

@login_required(login_url='login')
def itemview(request):
    viewitem=AddItem.objects.all()
    return render(request,'item_view.html',{'view':viewitem})


@login_required(login_url='login')
def additem(request):
    unit=Unit.objects.all()
    sale=Sales.objects.all()
    purchase=Purchase.objects.all()
    
    


  
    
        



    accounts = Purchase.objects.all()
    account_types = set(Purchase.objects.values_list('Account_type', flat=True))

    
    account = Sales.objects.all()
    account_type = set(Sales.objects.values_list('Account_type', flat=True))
    
    

    return render(request,'additem.html',{'unit':unit,'sale':sale,'purchase':purchase,
               
                            "account":account,"account_type":account_type,"accounts":accounts,"account_types":account_types,
                            
                            })

@login_required(login_url='login')
def add_account(request):
    if request.method=='POST':
        Account_type  =request.POST['acc_type']
        Account_name =request.POST['acc_name']
        Account_desc =request.POST['acc_desc']
       
        acc=Purchase(Account_type=Account_type,Account_name=Account_name,Account_desc=Account_desc)
        acc.save()                 
        return redirect("additem")
        
    return render(request,'additem.html')


@login_required(login_url='login')
def add(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            radio=request.POST.get('radio')
           
            
            if radio =='taxable':
                print('tax section')
                
    
                
                inter=request.POST['inter']
                intra=request.POST['intra']
                type=request.POST.get('type')
                name=request.POST['name']
                unit=request.POST['unit']
                hsn=request.POST['hsn']
                sel_price=request.POST.get('sel_price')
                sel_acc=request.POST.get('sel_acc')
                s_desc=request.POST.get('sel_desc')
                cost_price=request.POST.get('cost_price')
                cost_acc=request.POST.get('cost_acc')      
                p_desc=request.POST.get('cost_desc')
                tax=request.POST.get('radio')
                u=request.user.id
                us=request.user
                history="Created by" + str(us)
                user=User.objects.get(id=u)
                unit=Unit.objects.get(id=unit)
                sel=Sales.objects.get(id=sel_acc)
                cost=Purchase.objects.get(id=cost_acc)
                invacc=request.POST.get('invacc')
                    
                print(istock)
                    
                
                ad_item=AddItem(type=type,
                                Name=name,
                                p_desc=p_desc,
                                s_desc=s_desc,
                                s_price=sel_price,
                                p_price=cost_price,
                                tax=tax,
                                hsn=hsn,
                                unit=unit,
                                sales=sel,
                                purchase=cost,
                                user=user,
                                creat=history,
                                interstate=inter,
                                intrastate=intra,
                                invacc=invacc,
                                stock=istock
                                )
                ad_item.save()
                
            else:
                print('nontaxsection')
                                                  
                type=request.POST.get('type')
                name=request.POST['name']
                unit=request.POST['unit']
                hsn=request.POST['hsn']
                sel_price=request.POST.get('sel_price')
                sel_acc=request.POST.get('sel_acc')
                s_desc=request.POST.get('sel_desc')
                cost_price=request.POST.get('cost_price')
                cost_acc=request.POST.get('cost_acc')      
                p_desc=request.POST.get('cost_desc')
                tax=request.POST.get('radio')
                u=request.user.id
                us=request.user
                history="Created by" + str(us)
                user=User.objects.get(id=u)
                unit=Unit.objects.get(id=unit)
                sel=Sales.objects.get(id=sel_acc)
                cost=Purchase.objects.get(id=cost_acc)
                istock = request.POST['openstock']
               
                ad_item=AddItem(type=type,
                                Name=name,
                                hsn=hsn,
                                p_desc=p_desc,
                                s_desc=s_desc,
                                s_price=sel_price,
                                p_price=cost_price,
                                unit=unit,
                                sales=sel,
                                tax=tax,
                                purchase=cost,
                                user=user,
                                creat=history,
                                interstate='none',
                                intrastate='none',
                                stock=istock
                            
                               
                                )
                
                ad_item.save()
           
           
            return redirect("itemview")
    return render(request,'additem.html')



@login_required(login_url='login')
def edititem(request,id):
    pedit=AddItem.objects.get(id=id)
    p=Purchase.objects.all()
    s=Sales.objects.all()
    u=Unit.objects.all()

    accounts = Purchase.objects.all()
    account_types = set(Purchase.objects.values_list('Account_type', flat=True))
    

    
    account = Sales.objects.all()
    account_type = set(Sales.objects.values_list('Account_type', flat=True))
    
    return render(request,'edititem.html',{"account":account,"account_type":account_type,'e':pedit,'p':p,'s':s,'u':u,"accounts":accounts,"account_types":account_types})



@login_required(login_url='login')
def edit_db(request,id):
        if request.method=='POST':
            edit=AddItem.objects.get(id=id)
            edit.type=request.POST.get('type')
            edit.Name=request.POST['name']
            unit=request.POST['unit']
            edit.s_price=request.POST['sel_price']
            sel_acc=request.POST['sel_acc']
            edit.s_desc=request.POST['sel_desc']
            edit.p_price=request.POST['cost_price']
            cost_acc=request.POST['cost_acc']        
            edit.p_desc=request.POST['cost_desc']
            edit.hsn=request.POST['hsn']
            
            edit.unit=Unit.objects.get(id=unit)
            edit.sales=Sales.objects.get(id=sel_acc)
            edit.purchase=Purchase.objects.get(id=cost_acc)
            edit.save()
            return redirect('itemview')

        return render(request,'edititem.html')


@login_required(login_url='login')
def detail(request,id):
    user_id=request.user
    items=AddItem.objects.all()
    product=AddItem.objects.get(id=id)
    history=History.objects.filter(p_id=product.id)
    print(product.id)
    
    
    context={
       "allproduct":items,
       "product":product,
       "history":history,
      
    }
    
    return render(request,'demo.html',context)


@login_required(login_url='login')
def Action(request,id):
    user=request.user.id
    user=User.objects.get(id=user)
    viewitem=AddItem.objects.all()
    event=AddItem.objects.get(id=id)
    

    print(user)
    if request.method=='POST':
        action=request.POST['action']
        event.satus=action
        event.save()
        if action == 'active':
            History(user=user,message="Item marked as Active ",p=event).save()
        else:
            History(user=user,message="Item marked as inActive",p=event).save()
    return render(request,'item_view.html',{'view':viewitem})

@login_required(login_url='login')
def cleer(request,id):
    dl=AddItem.objects.get(id=id)
    dl.delete()
    return redirect('itemview')


@login_required(login_url='login')
def add_unit(request):
    if request.method=='POST':
        unit_name=request.POST['unit_name']
        Unit(unit=unit_name).save()
        return redirect('additem')
    return render(request,"additem.html")


@login_required(login_url='login')
def add_sales(request):
    if request.method=='POST':
        Account_type  =request.POST['acc_type']
        Account_name =request.POST['acc_name']
        Acount_code =request.POST['acc_code']
        Account_desc =request.POST['acc_desc']        
        acc=Sales(Account_type=Account_type,Account_name=Account_name,Acount_code=Acount_code,Account_desc=Account_desc)
        acc.save()
        return redirect('additem')
    return render(request,'additem.html')


@login_required(login_url='login')
def vendor(request):
    return render(request,'create_vendor.html')


@login_required(login_url='login')
def add_vendor(request):
    if request.method=="POST":
        vendor_data=vendor_table()
        vendor_data.salutation=request.POST['salutation']
        vendor_data.first_name=request.POST['first_name']
        vendor_data.last_name=request.POST['last_name']
        vendor_data.company_name=request.POST['company_name']
        vendor_data.vendor_display_name=request.POST['v_display_name']
        vendor_data.vendor_email=request.POST['vendor_email']
        vendor_data.vendor_wphone=request.POST['w_phone']
        vendor_data.vendor_mphone=request.POST['m_phone']
        vendor_data.skype_number=request.POST['skype_number']
        vendor_data.designation=request.POST['designation']
        vendor_data.department=request.POST['department']
        vendor_data.website=request.POST['website']
        vendor_data.gst_treatment=request.POST['gst']

        x=request.POST['gst']
        if x=="Unregistered Business-not Registered under GST":
            vendor_data.pan_number=request.POST['pan_number']
            vendor_data.gst_number="null"
        else:
            vendor_data.gst_number=request.POST['gst_number']
            vendor_data.pan_number=request.POST['pan_number']

        vendor_data.source_supply=request.POST['source_supply']
        vendor_data.currency=request.POST['currency']
        vendor_data.opening_bal=request.POST['opening_bal']
        vendor_data.payment_terms=request.POST['payment_terms']

        user_id=request.user.id
        udata=User.objects.get(id=user_id)
        vendor_data.user=udata
        vendor_data.battention=request.POST['battention']
        vendor_data.bcountry=request.POST['bcountry']
        vendor_data.baddress=request.POST['baddress']
        vendor_data.bcity=request.POST['bcity']
        vendor_data.bstate=request.POST['bstate']
        vendor_data.bzip=request.POST['bzip']
        vendor_data.bphone=request.POST['bphone']
        vendor_data.bfax=request.POST['bfax']

        vendor_data.sattention=request.POST['sattention']
        vendor_data.scountry=request.POST['scountry']
        vendor_data.saddress=request.POST['saddress']
        vendor_data.scity=request.POST['scity']
        vendor_data.sstate=request.POST['sstate']
        vendor_data.szip=request.POST['szip']
        vendor_data.sphone=request.POST['sphone']
        vendor_data.sfax=request.POST['sfax']
        vendor_data.save()
# .......................................................adding to remaks table.....................
        vdata=vendor_table.objects.get(id=vendor_data.id)
        vendor=vdata
        rdata=remarks_table()
        rdata.remarks=request.POST['remark']
        rdata.user=udata
        rdata.vendor=vdata
        rdata.save()


#  ...........................adding multiple rows of table to model  ........................................................       
        salutation =request.POST.getlist('salutation[]')
        first_name =request.POST.getlist('first_name[]')
        last_name =request.POST.getlist('last_name[]')
        email =request.POST.getlist('email[]')
        work_phone =request.POST.getlist('wphone[]')
        mobile =request.POST.getlist('mobile[]')
        skype_number =request.POST.getlist('skype[]')
        designation =request.POST.getlist('designation[]')
        department =request.POST.getlist('department[]') 
        vdata=vendor_table.objects.get(id=vendor_data.id)
        vendor=vdata
       

        if len(salutation)==len(first_name)==len(last_name)==len(email)==len(work_phone)==len(mobile)==len(skype_number)==len(designation)==len(department):
            mapped2=zip(salutation,first_name,last_name,email,work_phone,mobile,skype_number,designation,department)
            mapped2=list(mapped2)
            print(mapped2)
            for ele in mapped2:
                created = contact_person_table.objects.get_or_create(salutation=ele[0],first_name=ele[1],last_name=ele[2],email=ele[3],
                         work_phone=ele[4],mobile=ele[5],skype_number=ele[6],designation=ele[7],department=ele[8],user=udata,vendor=vendor)
        
       
                 
        return redirect('create_purchase_order')


        

def sample(request):
    print("hello")
    return redirect('base')

def view_vendor_list(request):
    user_id=request.user.id
    udata=User.objects.get(id=user_id)
    data=vendor_table.objects.filter(user=udata)
    return render(request,'vendor_list.html',{'data':data})

def view_vendor_details(request,pk):
    user_id=request.user.id
    udata=User.objects.get(id=user_id)
    vdata1=vendor_table.objects.filter(user=udata)
    vdata2=vendor_table.objects.get(id=pk)
    mdata=mail_table.objects.filter(vendor=vdata2)
    ddata=doc_upload_table.objects.filter(user=udata,vendor=vdata2)
    cmt_data=comments_table.objects.filter(user=udata,vendor=vdata2)

    return render(request,'vendor_details.html',{'vdata':vdata1,'vdata2':vdata2,'mdata':mdata,'ddata':ddata,'cmt_data':cmt_data})

def add_comment(request,pk):
    p=Purchase_Order.objects.get(id=pk)
    if request.method=='POST':
        comment=request.POST.get('comment')
        p.comments=comment
        p.save()
    return redirect('purchase_bill_view',pk)

def sendmail(request):
    if request.method=='POST':
       subject=request.POST['subject']
       messag=request.POST['messag']
       sendto=request.POST['sendto']
       send_mail(subject,messag,settings.EMAIL_HOST_USER,
                 [sendto],fail_silently=False)
       return redirect('view_customr')



def edit_vendor(request,pk):
    vdata=vendor_table.objects.get(id=pk)
    if remarks_table.objects.filter(vendor=vdata).exists() or contact_person_table.objects.filter(vendor=vdata).exists():
        if remarks_table.objects.filter(vendor=vdata).exists() and contact_person_table.objects.filter(vendor=vdata).exists():
            rdata=remarks_table.objects.get(vendor=vdata)
            pdata=contact_person_table.objects.filter(vendor=vdata)
            return render(request,'edit_vendor.html',{'vdata':vdata,'rdata':rdata,'pdata':pdata})
        else:
            if remarks_table.objects.filter(vendor=vdata).exists():
                rdata=remarks_table.objects.get(vendor=vdata)
                return render(request,'edit_vendor.html',{'vdata':vdata,'rdata':rdata})
            if contact_person_table.objects.filter(vendor=vdata).exists():
                pdata=contact_person_table.objects.filter(vendor=vdata)
                return render(request,'edit_vendor.html',{'vdata':vdata,'pdata':pdata})      
        
    else:
        return render(request,'edit_vendor.html',{'vdata':vdata})


def edit_vendor_details(request,pk):
    if request.method=='POST':
        vdata=vendor_table.objects.get(id=pk)
        vdata.salutation=request.POST['salutation']
        vdata.first_name=request.POST['first_name']
        vdata.last_name=request.POST['last_name']
        vdata.company_name=request.POST['company_name']
        vdata.vendor_display_name=request.POST['v_display_name']
        vdata.vendor_email=request.POST['vendor_email']
        vdata.vendor_wphone=request.POST['w_phone']
        vdata.vendor_mphone=request.POST['m_phone']
        vdata.skype_number=request.POST['skype_number']
        vdata.designation=request.POST['designation']
        vdata.department=request.POST['department']
        vdata.website=request.POST['website']
        vdata.gst_treatment=request.POST['gst']
        if vdata.gst_treatment=="Unregistered Business-not Registered under GST":
            vdata.pan_number=request.POST['pan_number']
            vdata.gst_number="null"
        else:
            vdata.gst_number=request.POST['gst_number']
            vdata.pan_number=request.POST['pan_number']

        vdata.source_supply=request.POST['source_supply']
        vdata.currency=request.POST['currency']
        vdata.opening_bal=request.POST['opening_bal']
        vdata.payment_terms=request.POST['payment_terms']

        vdata.battention=request.POST['battention']
        vdata.bcountry=request.POST['bcountry']
        vdata.baddress=request.POST['baddress']
        vdata.bcity=request.POST['bcity']
        vdata.bstate=request.POST['bstate']
        vdata.bzip=request.POST['bzip']
        vdata.bphone=request.POST['bphone']
        vdata.bfax=request.POST['bfax']

        vdata.sattention=request.POST['sattention']
        vdata.scountry=request.POST['scountry']
        vdata.saddress=request.POST['saddress']
        vdata.scity=request.POST['scity']
        vdata.sstate=request.POST['sstate']
        vdata.szip=request.POST['szip']
        vdata.sphone=request.POST['sphone']
        vdata.sfax=request.POST['sfax']

        vdata.save()
             # .................................edit remarks_table ..........................
        vendor=vdata
        user_id=request.user.id
        udata=User.objects.get(id=user_id)
        if remarks_table.objects.filter(vendor=vdata).exists():
            rdata=remarks_table.objects.get(vendor=vdata)
            rdata.remarks=request.POST['remark']
            rdata.save()
        else:
            rdata=remarks_table()
            rdata.remarks=request.POST["remark"]
            rdata.vendor=vendor
            rdata.user=udata
            rdata.save()

            # .......................contact_person_table................ deleting existing entries and inserting  ...............

        pdata=contact_person_table.objects.filter(vendor=vdata)
        salutation =request.POST.getlist('salutation[]')
        first_name =request.POST.getlist('first_name[]')
        last_name =request.POST.getlist('last_name[]')
        email =request.POST.getlist('email[]')
        work_phone =request.POST.getlist('wphone[]')
        mobile =request.POST.getlist('mobile[]')
        skype_number =request.POST.getlist('skype[]')
        designation =request.POST.getlist('designation[]')
        department =request.POST.getlist('department[]') 

        vdata=vendor_table.objects.get(id=vdata.id)
        vendor=vdata
        user_id=request.user.id
        udata=User.objects.get(id=user_id)

        # .....  deleting existing rows......
        pdata.delete()
        if len(salutation)==len(first_name)==len(last_name)==len(email)==len(work_phone)==len(mobile)==len(skype_number)==len(designation)==len(department):
            mapped2=zip(salutation,first_name,last_name,email,work_phone,mobile,skype_number,designation,department)
            mapped2=list(mapped2)
            print(mapped2)
            for ele in mapped2:
                created = contact_person_table.objects.get_or_create(salutation=ele[0],first_name=ele[1],last_name=ele[2],email=ele[3],
                         work_phone=ele[4],mobile=ele[5],skype_number=ele[6],designation=ele[7],department=ele[8],user=udata,vendor=vendor)
        



        return redirect("view_vendor_list")

def upload_document(request,pk):
    if request.method=='POST':
        user_id=request.user.id
        udata=User.objects.get(id=user_id)
        vdata=vendor_table.objects.get(id=pk)
        title=request.POST['title']
        document=request.FILES.get('file')
        doc_data=doc_upload_table(user=udata,vendor=vdata,title=title,document=document)
        doc_data.save()
        return redirect("view_vendor_list")

def download_doc(request,pk):
    document=get_object_or_404(doc_upload_table,id=pk)
    response=HttpResponse(document.document,content_type='application/pdf')
    response['Content-Disposition']=f'attachment; filename="{document.document.name}"'
    return response

def cancel_vendor(request):
    return redirect("vendor")

def delete_vendor(request,pk):
    if comments_table.objects.filter(vendor=pk).exists():
        user2=comments_table.objects.filter(vendor=pk)
        user2.delete()
    if mail_table.objects.filter(vendor=pk).exists():
        user3=mail_table.objects.filter(vendor=pk)
        user3.delete()
    if doc_upload_table.objects.filter(vendor=pk).exists():
        user4=doc_upload_table.objects.filter(vendor=pk)
        user4.delete()
    if contact_person_table.objects.filter(vendor=pk).exists():
        user5=contact_person_table.objects.filter(vendor=pk)
        user5.delete()
    if remarks_table.objects.filter(vendor=pk).exists():
        user6=remarks_table.objects.filter(vendor=pk)
        user6.delete()
    
    user1=vendor_table.objects.get(id=pk)
    user1.delete()
    return redirect("view_vendor_list")
    
    

# view functions for retainer invoice

@login_required(login_url='login')
def add_customer(request):
    sb=payment_terms.objects.all()
    return render(request,'customer.html',{'sb':sb})


@login_required(login_url='login')
def retainer_invoice(request):
    invoices=RetainerInvoice.objects.all()
    context={'invoices':invoices}
    return render(request,'retainer_invoice.html',context)



@login_required(login_url='login')
def add_invoice(request):
    customer=customer.objects.all()   
    context={'customer':customer,}    
    return render(request,'add_invoice.html',context)

@login_required(login_url='login')
def create_invoice_draft(request):
    
    if request.method=='POST':
        select=request.POST['select']
        customer_name=Customer.objects.get(id=select)
        retainer_invoice_number=request.POST['retainer-invoice-number']
        references=request.POST['references']
        retainer_invoice_date=request.POST['invoicedate']
        total_amount=request.POST.get('total')
        customer_notes=request.POST['customer_notes']
        terms_and_conditions=request.POST['terms']
    
        retainer_invoice=RetainerInvoice(
            customer_name=customer_name,retainer_invoice_number=retainer_invoice_number,refrences=references,retainer_invoice_date=retainer_invoice_date,total_amount=total_amount,customer_notes=customer_notes,terms_and_conditions=terms_and_conditions)
    
        retainer_invoice.save()
        

        description = request.POST.getlist('description[]')
        amount =request.POST.getlist('amount[]')
        if len(description)==len(amount):
            mapped = zip(description,amount)
            mapped=list(mapped)
            for ele in mapped:
                created = Retaineritems.objects.get_or_create(description=ele[0],amount=ele[1], retainer=retainer_invoice)
        else:
            pass

        return redirect('retainer_invoice')

            
        

         
@login_required(login_url='login')
def create_invoice_send(request):
    if request.method=='POST':
        select=request.POST['select']
        customer_name=Customer.objects.get(id=select)
        retainer_invoice_number=request.POST['retainer-invoice-number']
        references=request.POST['references']
        retainer_invoice_date=request.POST['invoicedate']
        total_amount=request.POST.get('total')
        customer_notes=request.POST['customer_notes']
        terms_and_conditions=request.POST['terms']
        retainer_invoice=RetainerInvoice(
        customer_name=customer_name,retainer_invoice_number=retainer_invoice_number,refrences=references,retainer_invoice_date=retainer_invoice_date,total_amount=total_amount,customer_notes=customer_notes,terms_and_conditions=terms_and_conditions,is_draft=False)
        retainer_invoice.save()

        description = request.POST.getlist('description[]')
        amount = request.POST.getlist('amount[]')
        if len(description)==len(amount):
            mapped = zip(description,amount)
            mapped=list(mapped)
            for ele in mapped:
                created = Retaineritems.objects.get_or_create(description=ele[0],amount=ele[1], retainer=retainer_invoice)
        else:
            pass
        return redirect('invoice_view',pk=retainer_invoice.id)



@login_required(login_url='login')
def invoice_view(request,pk):
    invoices=RetainerInvoice.objects.all()
    invoice=RetainerInvoice.objects.get(id=pk)
    item=Retaineritems.objects.filter(retainer=pk)

    context={'invoices':invoices,'invoice':invoice,'item':item}
    return render(request,'invoice_view.html',context)

@login_required(login_url='login')
def retainer_template(request,pk):
    invoice=RetainerInvoice.objects.get(id=pk)
    return render(request,'template.html',{'invoice':invoice})

@login_required(login_url='login')
def retainer_edit_page(request,pk):
    invoice=RetainerInvoice.objects.get(id=pk)
    customer=Customer.objects.all()
    items=Retaineritems.objects.filter(retainer=pk)
    context={'invoice':invoice, 'customer':customer,'items':items}
    return render(request,'retainer_invoice_edit.html', context)


@login_required(login_url='login')
def retainer_update(request,pk):

    if request.method=='POST':
        retainer_invoice=RetainerInvoice.objects.get(id=pk)
        select=request.POST['select']
        retainer_invoice.customer_name=Customer.objects.get(id=select)
        retainer_invoice.retainer_invoice_number=request.POST['retainer-invoice-number']
        retainer_invoice.refrences=request.POST['references']
        retainer_invoice.retainer_invoice_date=request.POST['invoicedate']
        retainer_invoice.total_amount=request.POST.get('total')
        retainer_invoice.customer_notes=request.POST['customer_notes']
        retainer_invoice.terms_and_conditions=request.POST['terms']
    
        retainer_invoice.save()
        
        descriptions=request.POST.getlist('description[]')
        amounts=request.POST.getlist('amount[]')
        # if len(descriptions)==len(amounts):
        #     mapped = zip(descriptions,amounts)
        #     mapped=list(mapped)
        #     for ele in mapped:
        #         created=Retaineritems.objects.filter(retainer=retainer_invoice).update(description=ele[0])
        # else:
        #     pass
        for i in range(len(descriptions)):
            description=descriptions[i]
            amount=amounts[i]
            obj,created=Retaineritems.objects.update_or_create(retainer=retainer_invoice,description=description,defaults={'amount':amount})
            obj.save()





        return redirect('retainer_invoice')

@login_required(login_url='login')
def mail_send(request,pk):

    if request.method=='POST':
        comments=request.POST.getlist('mailcomments')
        print(comments)
        files=request.FILES.getlist('files')
        email_to='alenantony32@gmail.com'
        subject='Retainer Invoice'
        message1=f'Please keep the attached\nretainer invoice for future use.\n\ncomments:\n'
        message2='' 

        for comment in comments:
            message2 += comment + '\n'

        messages=message1+message2    


        email=EmailMessage(
            subject=subject,
            body=messages,
            to=[email_to]
        )
        
        for file in files:
            email.attach(file.name, file.read(), file.content_type)

        email.send() 
        print('bottom') 
        retainer_invoice=RetainerInvoice.objects.get(id=pk)
        retainer_invoice.is_draft=False
        retainer_invoice.is_sent=True
        retainer_invoice.save()  
        return redirect('retainer_invoice')
    
    return redirect('retainer_invoice')

@login_required(login_url='login')
def retaineritem_delete(request,pk):
    print('delete')
    item = get_object_or_404(Retaineritems, id=pk)
    item.delete()
    print('deleted')
    return redirect('retainer_edit_page' ,pk=item.retainer.id)
    
@login_required(login_url='login')
def retainer_delete(request,pk):
    items=Retaineritems.objects.filter(retainer=pk)
    items.delete()
    retainer=RetainerInvoice.objects.get(id=pk)
    retainer.delete()
    return redirect('retainer_invoice')
        
            
def allestimates(request):
    user = request.user
    estimates = Estimates.objects.filter(user=user).order_by('-id')
    company = company_details.objects.get(user=user)
    context = {
        'estimates': estimates,
        'company': company,
    }
    # for i in estimates:
    #     print(i)

    return render(request, 'all_estimates.html', context)





def newestimate(request):
    user = request.user
    # print(user_id)
    company = company_details.objects.get(user=user)
    items = AddItem.objects.filter(user_id=user.id)
    customers = customer.objects.filter(user_id=user.id)
    estimates_count = Estimates.objects.count()
    next_count = estimates_count+1
    context = {'company': company,
               'items': items,
               'customers': customers,
               'count': next_count,
               }

    return render(request, 'new_estimate.html', context)


def itemdata_est(request):
    cur_user = request.user
    user = User.objects.get(id=cur_user.id)
    company = company_details.objects.get(user=user)
    # print(company.state)
    id = request.GET.get('id')
    cust = request.GET.get('cust')
    print(id)
    print(cust)

    item = AddItem.objects.get(Name=id, user=user)

    rate = item.p_price
    place = company.state
    gst = item.intrastate
    igst = item.interstate
    place_of_supply = customer.objects.get(
        customerName=cust, user=user).placeofsupply
    return JsonResponse({"status": " not", 'place': place, 'rate': rate, 'pos': place_of_supply, 'gst': gst, 'igst': igst})
    return redirect('/')


def createestimate(request):
    print('hi1')
    cur_user = request.user
    user = User.objects.get(id=cur_user.id)
    print('hi1')
    if request.method == 'POST':
        cust_name = request.POST['customer_name']
        est_number = request.POST['estimate_number']
        reference = request.POST['reference']
        est_date = request.POST['estimate_date']
        exp_date = request.POST['expiry_date']

        item = request.POST.getlist('item[]')
        quantity = request.POST.getlist('quantity[]')
        rate = request.POST.getlist('rate[]')
        discount = request.POST.getlist('discount[]')
        tax = request.POST.getlist('tax[]')
        amount = request.POST.getlist('amount[]')
        # print(item)
        # print(quantity)
        # print(rate)
        # print(discount)
        # print(tax)
        # print(amount)

        cust_note = request.POST['customer_note']
        sub_total = request.POST['subtotal']
        igst = request.POST['igst']
        sgst = request.POST['sgst']
        cgst = request.POST['cgst']
        tax_amnt = request.POST['total_taxamount']
        shipping = request.POST['shipping_charge']
        adjustment = request.POST['adjustment_charge']
        total = request.POST['total']
        tearms_conditions = request.POST['tearms_conditions']
        attachment = request.FILES.get('file')
        status = 'Draft'

        estimate = Estimates(user=user, customer_name=cust_name, estimate_no=est_number, reference=reference, estimate_date=est_date, 
                             expiry_date=exp_date, sub_total=sub_total,igst=igst,sgst=sgst,cgst=cgst,tax_amount=tax_amnt, shipping_charge=shipping,
                             adjustment=adjustment, total=total, status=status, customer_notes=cust_note, terms_conditions=tearms_conditions, 
                             attachment=attachment)
        estimate.save()

        if len(item) == len(quantity) == len(rate) == len(discount) == len(tax) == len(amount):
            mapped = zip(item, quantity, rate, discount, tax, amount)
            mapped = list(mapped)
            for element in mapped:
                created = EstimateItems.objects.get_or_create(
                    estimate=estimate, item_name=element[0], quantity=element[1], rate=element[2], discount=element[3], tax_percentage=element[4], amount=element[5])
    return redirect('newestimate')


def create_and_send_estimate(request):
    cur_user = request.user
    user = User.objects.get(id=cur_user.id)
    print("hello")
    if request.method == 'POST':
        cust_name = request.POST['customer_name']
        est_number = request.POST['estimate_number']
        reference = request.POST['reference']
        est_date = request.POST['estimate_date']
        exp_date = request.POST['expiry_date']

        item = request.POST.getlist('item[]')
        quantity1 = request.POST.getlist('quantity[]')
        quantity = [float(x) for x in quantity1]
        rate1 = request.POST.getlist('rate[]')
        rate = [float(x) for x in rate1]
        discount1 = request.POST.getlist('discount[]')
        discount = [float(x) for x in discount1]
        tax1 = request.POST.getlist('tax[]')
        tax = [float(x) for x in tax1]
        amount1 = request.POST.getlist('amount[]')
        amount = [float(x) for x in amount1]
        print(item)
        print(quantity)
        print(rate)
        print(discount)
        print(tax)
        print(amount)

        cust_note = request.POST['customer_note']
        sub_total = float(request.POST['subtotal'])
        igst = float(request.POST['igst'])
        sgst = float(request.POST['sgst'])
        cgst = float(request.POST['cgst'])
        tax_amnt = float(request.POST['total_taxamount'])
        shipping = float(request.POST['shipping_charge'])
        adjustment = float(request.POST['adjustment_charge'])
        total = float(request.POST['total'])
        tearms_conditions = request.POST['tearms_conditions']
        attachment = request.FILES.get('file')
        status = 'Sent'
        tot_in_string = str(total)

        estimate = Estimates(user=user, customer_name=cust_name, estimate_no=est_number, reference=reference, estimate_date=est_date, 
                             expiry_date=exp_date, sub_total=sub_total,igst=igst,sgst=sgst,cgst=cgst,tax_amount=tax_amnt, shipping_charge=shipping,
                             adjustment=adjustment, total=total, status=status, customer_notes=cust_note, terms_conditions=tearms_conditions, 
                             attachment=attachment)
        estimate.save()

        if len(item) == len(quantity) == len(rate) == len(discount) == len(tax) == len(amount):
            mapped = zip(item, quantity, rate, discount, tax, amount)
            mapped = list(mapped)
            for element in mapped:
                created = EstimateItems.objects.get_or_create(
                    estimate=estimate, item_name=element[0], quantity=element[1], rate=element[2], discount=element[3], tax_percentage=element[4], amount=element[5])

        cust_email = customer.objects.get(
            user=user, customerName=cust_name).customerEmail
        print(cust_email)
        subject = 'Estimate'
        message = 'Dear Customer,\n Your Estimate has been Saved for a total amount of: ' + tot_in_string
        recipient = cust_email
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient])

    return redirect('newestimate')

def estimateslip(request, est_id):
    user = request.user
    company = company_details.objects.get(user=user)
    all_estimates = Estimates.objects.filter(user=user)
    estimate = Estimates.objects.get(id=est_id)
    items = EstimateItems.objects.filter(estimate=estimate)
    context = {
        'company': company,
        'all_estimates':all_estimates,
        'estimate': estimate,
        'items': items,
    }
    return render(request, 'estimate_slip.html', context)




def editestimate(request,est_id):
    user = request.user
    company = company_details.objects.get(user=user)
    customers = customer.objects.filter(user_id=user.id)
    items = AddItem.objects.filter(user_id=user.id)
    estimate = Estimates.objects.get(id=est_id)
    est_items = EstimateItems.objects.filter(estimate=estimate)
    context = {
        'company': company,
        'estimate': estimate,
        'customers': customers,
        'items': items,
        'est_items': est_items,
    }
    return render(request, 'edit_estimate.html', context)

def updateestimate(request,pk):
    cur_user = request.user
    user = User.objects.get(id=cur_user.id)

    if request.method == 'POST':
        estimate = Estimates.objects.get(id=pk)
        estimate.user = user
        estimate.customer_name = request.POST['customer_name']
        estimate.estimate_no = request.POST['estimate_number']
        estimate.reference = request.POST['reference']
        estimate.estimate_date = request.POST['estimate_date']
        estimate.expiry_date = request.POST['expiry_date']

        estimate.customer_notes = request.POST['customer_note']
        estimate.sub_total = float(request.POST['subtotal'])
        estimate.tax_amount = float(request.POST['total_taxamount'])
        estimate.shipping_charge = float(request.POST['shipping_charge'])
        estimate.adjustment = float(request.POST['adjustment_charge'])
        estimate.total = float(request.POST['total'])
        estimate.terms_conditions = request.POST['tearms_conditions']
        estimate.status = 'Draft'

        old=estimate.attachment
        new=request.FILES.get('file')
        if old != None and new == None:
            estimate.attachment = old
        else:
            estimate.attachment = new

        estimate.save()

        item = request.POST.getlist('item[]')
        quantity1 = request.POST.getlist('quantity[]')
        quantity = [float(x) for x in quantity1]
        rate1 = request.POST.getlist('rate[]')
        rate = [float(x) for x in rate1]
        discount1 = request.POST.getlist('discount[]')
        discount = [float(x) for x in discount1]
        tax1 = request.POST.getlist('tax[]')
        tax = [float(x) for x in tax1]
        amount1 = request.POST.getlist('amount[]')
        amount = [float(x) for x in amount1]
        # print(item)
        # print(quantity)
        # print(rate)
        # print(discount)
        # print(tax)
        # print(amount)

        objects_to_delete = EstimateItems.objects.filter(estimate_id=estimate.id)
        objects_to_delete.delete()

        
        if len(item) == len(quantity) == len(rate) == len(discount) == len(tax) == len(amount):
            mapped = zip(item, quantity, rate, discount, tax, amount)
            mapped = list(mapped)
            for element in mapped:
                created = EstimateItems.objects.get_or_create(
                    estimate=estimate, item_name=element[0], quantity=element[1], rate=element[2], discount=element[3], tax_percentage=element[4], amount=element[5])
    return redirect('allestimates')

def converttoinvoice(request,est_id):
    user = request.user
    company = company_details.objects.get(user=user)
    estimate = Estimates.objects.get(id=est_id)
    items = EstimateItems.objects.filter(estimate=estimate)
    cust = customer.objects.get(customerName=estimate.customer_name,user=user)
    invoice_count = invoice.objects.count()
    next_no = invoice_count+1 
    inv = invoice(customer=cust,invoice_no=next_no,terms='null',order_no=estimate.estimate_no,
                      inv_date=estimate.estimate_date,due_date=estimate.expiry_date,igst=estimate.igst,cgst=estimate.cgst,
                      sgst=estimate.sgst,t_tax=estimate.tax_amount,subtotal=estimate.sub_total,grandtotal=estimate.total,
                      cxnote=estimate.customer_notes,file=estimate.attachment,terms_condition=estimate.terms_conditions,
                      status=estimate.status)
    inv.save()
    inv = invoice.objects.get(invoice_no=next_no,customer=cust)
    for item in items:
        items = invoice_item(product=item.item_name,quantity=item.quantity,hsn='null',tax=item.tax_percentage,
                             total=item.amount,desc=item.discount,rate=item.rate,inv=inv)
        items.save()
    return redirect('allestimates')

class EmailAttachementView(View):
    form_class = EmailForm
    template_name = 'newmail.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'email_form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            email = form.cleaned_data['email']
            files = request.FILES.getlist('attach')

            try:
                mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [email])
                for f in files:
                    mail.attach(f.name, f.read(), f.content_type)
                mail.send()
                return render(request, self.template_name, {'email_form': form, 'error_message': 'Sent email to %s'%email})
            except:
                return render(request, self.template_name, {'email_form': form, 'error_message': 'Either the attachment is too big or corrupt'})

        return render(request, self.template_name, {'email_form': form, 'error_message': 'Unable to send email. Please try again later'})



def add_customer_for_estimate(request):
   
    return render(request,'createinvoice.html',{'sb':sb})
    
def entr_custmr_for_estimate(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            type=request.POST.get('type')
            txtFullName=request.POST['txtFullName']
            cpname=request.POST['cpname']
           
            email=request.POST.get('myEmail')
            wphone=request.POST.get('wphone')
            mobile=request.POST.get('mobile')
            skname=request.POST.get('skname')
            desg=request.POST.get('desg')      
            dept=request.POST.get('dept')
            wbsite=request.POST.get('wbsite')

            gstt=request.POST.get('gstt')
            posply=request.POST.get('posply')
            tax1=request.POST.get('tax1')
            crncy=request.POST.get('crncy')
            obal=request.POST.get('obal')

            select=request.POST.get('pterms')
            pterms=payment_terms.objects.get(id=select)
            pterms=request.POST.get('pterms')

            plst=request.POST.get('plst')
            plang=request.POST.get('plang')
            fbk=request.POST.get('fbk')
            twtr=request.POST.get('twtr')
        
            atn=request.POST.get('atn')
            ctry=request.POST.get('ctry')
            
            addrs=request.POST.get('addrs')
            addrs1=request.POST.get('addrs1')
            bct=request.POST.get('bct')
            bst=request.POST.get('bst')
            bzip=request.POST.get('bzip')
            bpon=request.POST.get('bpon')
            bfx=request.POST.get('bfx')

            sal=request.POST.get('sal')
            ftname=request.POST.get('ftname')
            ltname=request.POST.get('ltname')
            mail=request.POST.get('mail')
            bworkpn=request.POST.get('bworkpn')
            bmobile=request.POST.get('bmobile')

            bskype=request.POST.get('bskype')
            bdesg=request.POST.get('bdesg')
            bdept=request.POST.get('bdept')
            u = User.objects.get(id = request.user.id)

          
            ctmr=customer(customerName=txtFullName,customerType=type,
                        companyName=cpname,customerEmail=email,customerWorkPhone=wphone,
                         customerMobile=mobile,skype=skname,designation=desg,department=dept,
                           website=wbsite,GSTTreatment=gstt,placeofsupply=posply, Taxpreference=tax1,
                             currency=crncy,OpeningBalance=obal,PaymentTerms=pterms,
                                PriceList=plst,PortalLanguage=plang,Facebook=fbk,Twitter=twtr,
                                 Attention=atn,country=ctry,Address1=addrs,Address2=addrs1,
                                  city=bct,state=bst,zipcode=bzip,phone1=bpon,
                                   fax=bfx,CPsalutation=sal,Firstname=ftname,
                                    Lastname=ltname,CPemail=mail,CPphone=bworkpn,
                                    CPmobile= bmobile,CPskype=bskype,CPdesignation=bdesg,
                                     CPdepartment=bdept,user=u )
            ctmr.save()  
            
            return redirect("newestimate")
        return redirect("newestimate")
    
def payment_term_for_estimate(request):
    if request.method=='POST':
        term=request.POST.get('term')
        day=request.POST.get('day')
        ptr=payment_terms(Terms=term,Days=day)
        ptr.save()
        return redirect("add_customer_for_estimate")

    
@login_required(login_url='login')

def payment_term(request):
    if request.method=='POST':
        term=request.POST.get('term')
        day=request.POST.get('day')
        ptr=payment_terms(Terms=term,Days=day)
        ptr.save()
        return redirect("add_customer")

@login_required(login_url='login')

def invoiceview(request):
    invoicev=invoice.objects.all()
    
    if not payment_terms.objects.filter(Terms='net 15').exists(): 
       payment_terms(Terms='net 15',Days=15).save()
    if not payment_terms.objects.filter(Terms='due end of month').exists():
        payment_terms(Terms='due end of month',Days=60).save()
    elif not  payment_terms.objects.filter(Terms='net 30').exists():
        payment_terms(Terms='net 30',Days=30).save() 
    
    
    context={
        'invoice':invoicev,
        
    }
    return render(request,'invoiceview.html',context)

@login_required(login_url='login')

def detailedview(request,id):
    inv_dat=invoice.objects.all()
    inv_master=invoice.objects.get(id=id)
    invoiceitem=invoice_item.objects.filter(inv_id=id)
    company=company_details.objects.get(user_id=request.user.id)
    
    
    context={
        'inv_dat':inv_dat,
        'invoiceitem':invoiceitem,
        'comp':company,
        'invoice':inv_master,
        
                    }
    return render(request,'invoice_det.html',context)



@login_required(login_url='login')

def dele(request,pk):
    d=invoice.objects.get(id=pk)
    d.delete()
    return redirect('invoiceview')

@login_required(login_url='login')

def addinvoice(request):
    c=customer.objects.all()
    p=AddItem.objects.all()
    i=invoice.objects.all()
    pay=payment.objects.all()
    if not payment.objects.filter(term='net 15').exists(): 
       payment(term='net 15',days=15).save()
    if not payment.objects.filter(term='due end of month').exists():
        payment(term='due end of month',days=60).save()
    elif not  payment.objects.filter(term='net 30').exists():
        payment(term='net 30',days=30).save() 
    


    
            
            
            
            
    context={
        'c':c,
        'p':p,
        'i':i,
        'pay':pay,
        
    }
       
    return render(request,'createinvoice.html',context)


@login_required(login_url='login')

def add_prod(request):
    c=customer.objects.all()
    p=AddItem.objects.all()
    i=invoice.objects.all()
    pay=payment_terms.objects.all()
    if not payment_terms.objects.filter(Terms='net 15').exists(): 
       payment_terms(Terms='net 15',Days=15).save()
    if not payment_terms.objects.filter(Terms='due end of month').exists():
        payment_terms(Terms='due end of month',Days=60).save()
    elif not  payment_terms.objects.filter(Terms='net 30').exists():
        payment_terms(Terms='net 30',Days=30).save() 
    
    
   
    if request.user.is_authenticated:
        if request.method=='POST':
            c=request.POST['cx_name']
            cus=customer.objects.get(customerName=c) 
            print(cus.id)  
            custo=cus.id
            invoice_no=request.POST['inv_no']
            terms=request.POST['term']
            term=payment_terms.objects.get(id=terms)
            order_no=request.POST['ord_no']
            inv_date=request.POST['inv_date']
            due_date=request.POST['due_date']
        
            
            cxnote=request.POST['customer_note']
            subtotal=request.POST['subtotal']
            igst=request.POST['igst']
            cgst=request.POST['cgst']
            sgst=request.POST['sgst']
            totaltax=request.POST['totaltax']
            t_total=request.POST['t_total']
            if request.FILES.get('file') is not None:
                file=request.FILES['file']
            else:
                file="/static/images/alt.jpg"
            tc=request.POST['ter_cond']

            status=request.POST['sd']
            if status=='draft':
                print(status)   
            else:
                print(status)  
        
            product=request.POST.getlist('item[]')
            hsn=request.POST.getlist('hsn[]')
            quantity=request.POST.getlist('quantity[]')
            rate=request.POST.getlist('rate[]')
            desc=request.POST.getlist('desc[]')
            tax=request.POST.getlist('tax[]')
            total=request.POST.getlist('amount[]')
            term=payment_terms.objects.get(id=term.id)

            inv=invoice(customer_id=custo,invoice_no=invoice_no,terms=term,order_no=order_no,inv_date=inv_date,due_date=due_date,
                        cxnote=cxnote,subtotal=subtotal,igst=igst,cgst=cgst,sgst=sgst,t_tax=totaltax,
                        grandtotal=t_total,status=status,terms_condition=tc,file=file)
            inv.save()
            inv_id=invoice.objects.get(id=inv.id)
            if len(product)==len(hsn)==len(quantity)==len(desc)==len(tax)==len(total)==len(rate):

                mapped = zip(product,hsn,quantity,desc,tax,total,rate)
                mapped = list(mapped)
                for element in mapped:
                    created = invoice_item.objects.get_or_create(inv=inv_id,product=element[0],hsn=element[1],
                                        quantity=element[2],desc=element[3],tax=element[4],total=element[5],rate=element[6])
                    
                return redirect('invoiceview')
    context={
            'c':c,
            'p':p,
            'i':i,
            'pay':pay,
    }       
    return render(request,'createinvoice.html',context)


@login_required(login_url='login')

def add_payment(request):
    if request.method=='POST':
            terms=request.POST.get()
    return redirect('add_prod')


@login_required(login_url='login')

def add_cx(request):
    if request.user.is_authenticated:
        if request.method=='POST':
                user=request.user.id
                user=User.objects.get(id=user)
                print(user)
                name=request.POST.get('name')
                email=request.POST.get('email')
                pos=request.POST.get('position')
                state=request.POST.get('state')
                com_name=request.POST.get('company')
                customer(customerName=name,customerEmail=email,placeofsupply=pos,state=state,companyName=com_name,user_id=user.id).save()
        return redirect('add_prod')




@login_required(login_url='login')

def edited_prod(request,id):
    print(id)
    c = customer.objects.all()
    p = AddItem.objects.all()
    invoiceitem = invoice_item.objects.filter(inv_id=id)
    invoic = invoice.objects.get(id=id)
    pay=payment_terms.objects.all()
  
    if request.method == 'POST':
        u=request.user.id
        c=request.POST['cx_name']
        
        cust=customer.objects.get(customerName=c) 
        invoic.customer=cust
        term=request.POST['term']
        
        
        invoic.terms = payment_terms.objects.get(id=term)
        invoic.inv_date = request.POST['inv_date']
        invoic.due_date = request.POST['due_date']
        invoic.cxnote = request.POST['customer_note']
        invoic.subtotal = request.POST['subtotal']
        invoic.igst = request.POST['igst']
        invoic.cgst = request.POST['cgst']
        invoic.sgst = request.POST['sgst']
        invoic.t_tax = request.POST['totaltax']
        invoic.grandtotal = request.POST['t_total']

        if request.FILES.get('file') is not None:
            invoic.file = request.FILES['file']
        else:
            invoic.file = "/static/images/alt.jpg"

            invoic.terms_condition = request.POST.get('ter_cond')
        
        status=request.POST['sd']
        if status=='draft':
            invoic.status=status      
        else:
            invoic.status=status   
         
        invoic.save()
        
        print("/////////////////////////////////////////////////////////")
        product=request.POST.getlist('item[]')
        hsn=request.POST.getlist('hsn[]')
        quantity=request.POST.getlist('quantity[]')
        rate=request.POST.getlist('rate[]')
        desc=request.POST.getlist('desc[]')
        tax=request.POST.getlist('tax[]')
        total=request.POST.getlist('amount[]')
        obj_dele=invoice_item.objects.filter(inv_id=invoic.id)
        obj_dele.delete()
       
        if len(product)==len(hsn)==len(quantity)==len(desc)==len(tax)==len(total)==len(rate):

            mapped = zip(product,hsn,quantity,desc,tax,total,rate)
            mapped = list(mapped)
            for element in mapped:
                created = invoice_item.objects.get_or_create(inv=invoic,product=element[0],hsn=element[1],
                                    quantity=element[2],desc=element[3],tax=element[4],total=element[5],rate=element[6])
                
            return redirect('detailedview',id)
                    
    context = {
            'c': c,
            'p': p,
            'inv': invoiceitem,
            'i': invoic,
            'pay':pay,
        }             
        
    return render(request, 'invoiceedit.html', context)





@login_required(login_url='login')

def edited(request,id):
    c=customer.objects.all()
    p=AddItem.objects.all()
    invoiceitem=invoice_item.objects.filter(inv_id=id)
    inv=invoice.objects.get(id=id)
    context={
        'c':c,
        'p':p,
        'inv':invoiceitem,
        'inv':inv,
        
    }
    
    return render(request,'editinvoice.html')



@login_required(login_url='login')

def itemdata(request):
    cur_user = request.user.id
    user = User.objects.get(id=cur_user)
    company = company_details.objects.get(user = user)
    # print(company.state)
    id = request.GET.get('id')
    cust = request.GET.get('cust')
    
        
    item = AddItem.objects.get(Name=id)
    cus=customer.objects.get(customerName=cust)
    rate = item.s_price
    place=company.state
    gst = item.intrastate
    igst = item.interstate
    desc=item.s_desc
    print(place)
    mail=cus.customerEmail
    
    place_of_supply = customer.objects.get(customerName=cust).placeofsupply
    print(place_of_supply)
    return JsonResponse({"status":" not",'mail':mail,'desc':desc,'place':place,'rate':rate,'pos':place_of_supply,'gst':gst,'igst':igst})
    return redirect('/')
    

def deleteestimate(request,est_id):
    user = request.user
    company = company_details.objects.get(user=user)
    estimate = Estimates.objects.get(id=est_id)
    items = EstimateItems.objects.filter(estimate=estimate)
    items.delete()
    estimate.delete()
    return redirect('allestimates')
    

@login_required(login_url='login')
def additem_page_est(request):
    unit=Unit.objects.all()
    sale=Sales.objects.all()
    purchase=Purchase.objects.all()
    accounts = Purchase.objects.all()
    account_types = set(Purchase.objects.values_list('Account_type', flat=True))

    
    account = Sales.objects.all()
    account_type = set(Sales.objects.values_list('Account_type', flat=True))
    
    

    return render(request,'additem_est.html',{'unit':unit,'sale':sale,'purchase':purchase,
               
                            "account":account,"account_type":account_type,"accounts":accounts,"account_types":account_types,
                            
                            })

def additem_est(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            radio=request.POST.get('radio')
            if radio=='tax':
    
                
                inter=request.POST['inter']
                intra=request.POST['intra']
                type=request.POST.get('type')
                name=request.POST['name']
                unit=request.POST['unit']
                sel_price=request.POST.get('sel_price')
                sel_acc=request.POST.get('sel_acc')
                s_desc=request.POST.get('sel_desc')
                cost_price=request.POST.get('cost_price')
                cost_acc=request.POST.get('cost_acc')      
                p_desc=request.POST.get('cost_desc')
                u=request.user.id
                us=request.user
                history="Created by" + str(us)
                user=User.objects.get(id=u)
                unit=Unit.objects.get(id=unit)
                sel=Sales.objects.get(id=sel_acc)
                cost=Purchase.objects.get(id=cost_acc)
                ad_item=AddItem(type=type,Name=name,p_desc=p_desc,s_desc=s_desc,s_price=sel_price,p_price=cost_price,unit=unit,
                            sales=sel,purchase=cost,user=user,creat=history,interstate=inter,intrastate=intra
                                )
                
            else:
                                                  
                type=request.POST.get('type')
                name=request.POST['name']
                unit=request.POST['unit']
                sel_price=request.POST.get('sel_price')
                sel_acc=request.POST.get('sel_acc')
                s_desc=request.POST.get('sel_desc')
                cost_price=request.POST.get('cost_price')
                cost_acc=request.POST.get('cost_acc')      
                p_desc=request.POST.get('cost_desc')
                u=request.user.id
                us=request.user
                history="Created by" + str(us)
                user=User.objects.get(id=u)
                unit=Unit.objects.get(id=unit)
                sel=Sales.objects.get(id=sel_acc)
                cost=Purchase.objects.get(id=cost_acc)
                ad_item=AddItem(type=type,Name=name,p_desc=p_desc,s_desc=s_desc,s_price=sel_price,p_price=cost_price,unit=unit,
                            sales=sel,purchase=cost,user=user,creat=history,interstate='none',intrastate='none'
                                )
                ad_item.save()
            ad_item.save()
           
            return redirect("newestimate")
    return render(request,'additem_est.html')

@login_required(login_url='login')
def add_unit_est(request):
    if request.method=='POST':
        unit_name=request.POST['unit_name']
        Unit(unit=unit_name).save()
        return redirect('additem_est')
    return redirect("additem_est")
    
#-------------new view functions to add

@login_required(login_url='login')
def add_sales_est(request):
    if request.method=='POST':
        Account_type  =request.POST['acc_type']
        Account_name =request.POST['acc_name']
        Acount_code =request.POST['acc_code']
        Account_desc =request.POST['acc_desc']        
        acc=Sales(Account_type=Account_type,Account_name=Account_name,Acount_code=Acount_code,Account_desc=Account_desc)
        acc.save()
        return redirect('additem_est')
    return redirect("additem_est")

@login_required(login_url='login')
def add_account_est(request):
    if request.method=='POST':
        Account_type  =request.POST['acc_type']
        Account_name =request.POST['acc_name']
        Acount_code =request.POST['acc_code']
        Account_desc =request.POST['acc_desc']
       
        acc=Purchase(Account_type=Account_type,Account_name=Account_name,Acount_code=Acount_code,Account_desc=Account_desc)
        acc.save()                 
        return redirect("additem_est")
        
    return redirect("additem_est")
    
def customerdata(request):
    customer_id = request.GET.get('id')
    print(customer_id)
    cust = customer.objects.get(customerName=customer_id)
    data7 = {'email': cust.customerEmail}
    
    print(data7)
    return JsonResponse(data7)


def add_customer_for_invoice(request):
    pt=payment_terms.objects.all()
    if request.user.is_authenticated:
        if request.method=='POST':
            type=request.POST.get('type')
            txtFullName=request.POST['txtFullName']
            cpname=request.POST['cpname']
           
            email=request.POST.get('myEmail')
            wphone=request.POST.get('wphone')
            mobile=request.POST.get('mobile')
            skname=request.POST.get('skname')
            desg=request.POST.get('desg')      
            dept=request.POST.get('dept')
            wbsite=request.POST.get('wbsite')

            gstt=request.POST.get('gstt')
            posply=request.POST.get('posply')
            tax1=request.POST.get('tax1')
            crncy=request.POST.get('crncy')
            obal=request.POST.get('obal')

            select=request.POST.get('pterms')
            pterms=payment_terms.objects.get(id=select)
            pterms=request.POST.get('pterms')

            plst=request.POST.get('plst')
            plang=request.POST.get('plang')
            fbk=request.POST.get('fbk')
            twtr=request.POST.get('twtr')
        
            atn=request.POST.get('atn')
            ctry=request.POST.get('ctry')
            
            addrs=request.POST.get('addrs')
            addrs1=request.POST.get('addrs1')
            bct=request.POST.get('bct')
            bst=request.POST.get('bst')
            bzip=request.POST.get('bzip')
            bpon=request.POST.get('bpon')
            bfx=request.POST.get('bfx')

            sal=request.POST.get('sal')
            ftname=request.POST.get('ftname')
            ltname=request.POST.get('ltname')
            mail=request.POST.get('mail')
            bworkpn=request.POST.get('bworkpn')
            bmobile=request.POST.get('bmobile')

            bskype=request.POST.get('bskype')
            bdesg=request.POST.get('bdesg')
            bdept=request.POST.get('bdept')
            u = User.objects.get(id = request.user.id)

          
            ctmr=customer(customerName=txtFullName,customerType=type,
                        companyName=cpname,customerEmail=email,customerWorkPhone=wphone,
                         customerMobile=mobile,skype=skname,designation=desg,department=dept,
                           website=wbsite,GSTTreatment=gstt,placeofsupply=posply, Taxpreference=tax1,
                             currency=crncy,OpeningBalance=obal,PaymentTerms=pterms,
                                PriceList=plst,PortalLanguage=plang,Facebook=fbk,Twitter=twtr,
                                 Attention=atn,country=ctry,Address1=addrs,Address2=addrs1,
                                  city=bct,state=bst,zipcode=bzip,phone1=bpon,
                                   fax=bfx,CPsalutation=sal,Firstname=ftname,
                                    Lastname=ltname,CPemail=mail,CPphone=bworkpn,
                                    CPmobile= bmobile,CPskype=bskype,CPdesignation=bdesg,
                                     CPdepartment=bdept,user=u )
            ctmr.save()  
            
            return redirect("add_prod")
        return render(request,"createinvoice.html",)
        
        
def payment_term_for_invoice(request):
    if request.method=='POST':
        term=request.POST.get('term')
        day=request.POST.get('day')
        ptr=payment_terms(Terms=term,Days=day)
        ptr.save()
        return redirect("add_prod")
        
        
def addprice(request):
    add=AddItem.objects.all()
    return render(request,'addprice_list.html',{'add':add})
def addpl(request):
    print('hi')
    if request.method == "POST":
        

        
        name = request.POST.get('name')
        print(name)
        types = request.POST.get('type')
        print(types)
        taxes=request.POST.get('rate')
        desc = request.POST.get('desc')
        cur = request.POST.get('currency')
        print(cur)
        mark = request.POST.get('mark')
        print(mark)
        perc = request.POST.get('per')
        print(perc)
        rounds = request.POST.get('round')
        print(rounds)
        u = request.user.id
        user = User.objects.get(id=u)
            
        ad_item = Pricelist(
                name=name,
                types=types,
                tax=taxes,
                currency=cur,
                description=desc,
                mark=mark,
                percentage=perc,
                roundoff=rounds,
                user=user,
            )
            
        ad_item.save()
        item_name = request.POST.getlist('iname[]') 
        print(item_name)
        price = request.POST.getlist('iprice[]')
        rate = request.POST.getlist('custom[]') 
        if len(item_name) == len(price) == len(rate):
            mapped2 = zip(item_name, price, rate)
            mapped2 = list(mapped2)
         
            for ele in mapped2:
                created = Sample_table.objects.get_or_create(item_name=ele[0], price=ele[1], cust_rate=ele[2], pl=ad_item)

        return redirect("viewpricelist")
    else:
        # Handle the case when the request method is not POST
        return render(request, 'addprice_list.html')
    # return render(request, 'addprice_list.html')
def createpl(request):
    return render(request,'addprice_list.html')
def active_status(request, id):
    user = request.user.id
    user = User.objects.get(id=user)
    viewitem = Pricelist.objects.all()
    event = Pricelist.objects.get(id=id)
    
    if request.method == 'POST':
        action = request.POST['action']
        event.status = action  # Updated field name to 'status'
        event.save()
    
    return render(request, 'view_price_list.html', {'view': viewitem})

def viewpricelist(request):
    view=Pricelist.objects.all()                                                                                                                                                                                                                                                                                                                        
    return render(request,'view_price_list.html',{'view':view})
def viewlist(request,id):
    user_id=request.user
    items=Pricelist.objects.all()
    product=Pricelist.objects.get(id=id)
    print(product.id)
    
    
    context={
       "allproduct":items,
       "product":product,
      
    }
    
    return render(request,'list.html',context)

def editlist(request,id):
    editpl=Pricelist.objects.get(id=id)
    sam=Sample_table.objects.filter(pl=id)
    return render(request,'edit_pricelist.html',{'editpl':editpl,'sam':sam})
def editpage(request,id):
    if request.method=='POST':
        edit=Pricelist.objects.get(id=id)
        edit.name=request.POST['name']
        edit.description=request.POST['desc']
        edit.mark=request.POST['mark']
        edit.percentage=request.POST['per']
        print(request.POST['per'])
        edit.tax=request.POST['types']
        
        edit.roundoff=request.POST['round']
        print(edit.roundoff)
        item_name = request.POST.getlist('iname[]') 
        print(item_name)
        price = request.POST.getlist('iprice[]')
        rate = request.POST.getlist('custom[]') 
        sam=Sample_table.objects.filter(pl=id).delete()

        if len(item_name) == len(price) == len(rate):
            mapped2 = zip(item_name, price, rate)
            mapped2 = list(mapped2)
         
            for ele in mapped2:
                created = Sample_table.objects.get_or_create(item_name=ele[0], price=ele[1], cust_rate=ele[2],pl=edit)
        edit.save()

        return redirect('viewpricelist')
def delete_item(request,id):
    dl=Pricelist.objects.get(id=id)
    dl.delete()
    return redirect('viewpricelist')


def banking_home(request):
    company = company_details.objects.get(user = request.user)
    viewitem=banking.objects.filter(user=request.user)
    return render(request,'banking.html',{'view':viewitem,"company":company})       
    
def create_banking(request):
    company = company_details.objects.get(user = request.user)
    print(company.company_name)
    banks = bank.objects.filter(user=request.user, acc_type="bank")
    return render(request,'create_banking.html',{"bank":banks,"company":company})    

def save_banking(request):
    if request.method == "POST":
        a=banking()
        a.name = request.POST.get('main_name',None)
        a.alias = request.POST.get('main_alias',None)
        a.acc_type = request.POST.get('main_type',None)
        a.ac_holder = request.POST.get('ac_holder',None)
        a.ac_no = request.POST.get('ac_number',None)
        a.ifsc = request.POST.get('ifsc',None)
        a.swift_code = request.POST.get('sw_code',None)
        a.bnk_name = request.POST.get('bnk_nm',None)
        a.bnk_branch = request.POST.get('br_name',None)
        a.chq_book = request.POST.get('alter_chq',None)
        a.chq_print = request.POST.get('en_chq',None)
        a.chq_config = request.POST.get('chq_prnt',None)
        a.mail_name = request.POST.get('name',None)
        a.mail_addr = request.POST.get('address',None)
        a.mail_country = request.POST.get('country',None)
        a.mail_state = request.POST.get('state',None)
        a.mail_pin = request.POST.get('pin',None)
        a.bd_bnk_det = request.POST.get('bnk_det',None)
        a.bd_pan_no = request.POST.get('pan',None)
        a.bd_reg_typ = request.POST.get('register_type',None)
        a.bd_gst_no = request.POST.get('gstin',None)
        a.bd_gst_det = request.POST.get('gst_det',None)
        a.opening_blnc_type = request.POST.get('opening_blnc_type',None)
        a.user=request.user
        a.opening_bal = request.POST.get('balance',None)
        a.save()
        return redirect("banking_home")
    return redirect("create_banking")

def view_bank(request,id):
    viewitem=banking.objects.filter(user=request.user)
    bnk=banking.objects.get(id=id,user=request.user)
    company = company_details.objects.get(user = request.user)
    context={
        'view':viewitem,
        'bnk':bnk,
        "company":company
    }
    return render(request,"view_bank.html",context)

def banking_edit(request,id):
    bnk=banking.objects.get(id=id,user=request.user)
    banks = bank.objects.filter(user=request.user, acc_type="bank")
    company = company_details.objects.get(user = request.user)
    context={
        'bnk':bnk,
        "bank":banks,
        "company":company
    }
    return render(request,"edit_banking.html",context)

def save_edit_bnk(request,id):
    if request.method == "POST":
        a=banking.objects.get(id=id,user=request.user)
        a.name = request.POST.get('main_name',None)
        a.alias = request.POST.get('main_alias',None)
        a.acc_type = request.POST.get('main_type',None)
        a.ac_holder = request.POST.get('ac_holder',None)
        a.ac_no = request.POST.get('ac_number',None)
        a.ifsc = request.POST.get('ifsc',None)
        a.swift_code = request.POST.get('sw_code',None)
        a.bnk_name = request.POST.get('bnk_nm',None)
        a.bnk_branch = request.POST.get('br_name',None)
        a.chq_book = request.POST.get('alter_chq',None)
        a.chq_print = request.POST.get('en_chq',None)
        a.chq_config = request.POST.get('chq_prnt',None)
        a.mail_name = request.POST.get('name',None)
        a.mail_addr = request.POST.get('address',None)
        a.mail_country = request.POST.get('country',None)
        a.mail_state = request.POST.get('state',None)
        a.mail_pin = request.POST.get('pin',None)
        a.bd_bnk_det = request.POST.get('bnk_det',None)
        a.bd_pan_no = request.POST.get('pan',None)
        a.bd_reg_typ = request.POST.get('register_type',None)
        a.bd_gst_no = request.POST.get('gstin',None)
        a.bd_gst_det = request.POST.get('gst_det',None)
        a.opening_bal = request.POST.get('balance',None)
        a.opening_blnc_type = request.POST.get('opening_blnc_type',None)
        a.save()
        return redirect("banking_home")
    return redirect("create_banking")

def save_bank(request):
    if request.method == "POST":
        a=bank()
        a.acc_type = request.POST.get('type',None)
        a.bank_name = request.POST.get('bank',None)
        a.user = request.user
        a.save()
        return redirect("create_banking")
    return redirect("create_banking")
def save_banking_edit(request,id):
    if request.method == "POST":
        a=bank()
        a.acc_type = request.POST.get('type',None)
        a.bank_name = request.POST.get('bank',None)
        a.user = request.user
        a.save()
        return redirect("banking_edit", id)
    return redirect("banking_edit", id)
    
def basenav(request):
    company = company_details.objects.get(user = request.user)
    print(company.company_name)
    context = {
                'company' : company
            }
    return render(request,'base.html',context)

def banking_delete(request,id):
    bnk=banking.objects.get(id=id)
    bnk.delete()
    return redirect("banking_home")
    
@login_required(login_url='login')
def recurringhome(request):
    selected_vendor_id = request.GET.get('vendor')
    vendors = vendor_table.objects.filter(user=request.user)
    selected_vendor = vendor_table.objects.filter(id=selected_vendor_id).first()
    gst_number = selected_vendor.gst_number if selected_vendor else ''
    return render(request, 'recurring_home.html', {
        'vendors': vendors,
        'selected_vendor_id': selected_vendor_id,
        'gst_number': gst_number,
    })




from django.shortcuts import get_object_or_404
from .models import Expense, vendor_table

def add_expense(request):
    if request.method == 'POST':
        profile_name = request.POST['profile_name']
        repeat_every = request.POST['repeat_every']
        start_date = request.POST['start_date']
        ends_on = request.POST['ends_on']
        expense_account = request.POST.get('expense_account', '')  # Use get() with a default value
        expense_type = request.POST['expense_type']
        goods_label = request.POST.get('goods_label')
        amount = request.POST['amount']
        currency = request.POST['currency']
        paidthrough = request.POST['paidthrough']
        vendor_id = request.POST['vendor']
        vendor = get_object_or_404(vendor_table, pk=vendor_id)
        gst = request.POST['gst']
        destination = request.POST['destination']
        tax = request.POST['tax']
        notes = request.POST['notes']
        customer_id = request.POST['customername']
        customer_obj = get_object_or_404(customer, pk=customer_id)
        expense = Expense(
            profile_name=profile_name, repeat_every=repeat_every, start_date=start_date,
            ends_on=ends_on, expense_account=expense_account, expense_type=expense_type,
            goods_label=goods_label, amount=amount, currency=currency, paidthrough=paidthrough,
            vendor=vendor, gst=gst, customername=customer_obj.customerName,
            notes=notes, tax=tax, destination=destination
        )
        expense.save()
        return redirect('recurringbase')
    else:
        vendors = vendor_table.objects.all()
        return render(request, 'add_expense.html', {'vendors': vendors})


@login_required(login_url='login')
def recurringbase(request):
    expenses = Expense.objects.all()
    return render(request, 'recurring_base.html',{'expenses': expenses})

def show_recurring(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expenses = Expense.objects.all()

    search_query = request.GET.get('search_query')
    search_date = request.GET.get('search_date')

    if search_query:
        expenses = expenses.filter(
            Q(profile_name_icontains=search_query) | Q(customername_icontains=search_query)
        )
    
    if search_date:
        expenses = expenses.filter(start_date=search_date)

    if request.method == 'POST':
        comments = request.POST.get('enter_comment_here', '')
        Comment.objects.create(profile_name=expense.profile_name, expense=expense, comment=comments)

    comments = Comment.objects.filter(profile_name=expense.profile_name, expense=expense)

    return render(request, 'show_recurring.html', {'expense': expense, 'expenses': expenses, 'comments': comments})


def expense_details(request):
    expenses = Expense.objects.all()
    return render(request, 'recurring_base.html',{'expenses': expenses})
    
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    vendors = vendor_table.objects.all()
    customers = customer.objects.all()  # Fetch all customers

    if request.method == 'POST':
        expense.profile_name = request.POST.get('profile_name')
        expense.repeat_every = request.POST.get('repeat_every')
        expense.start_date = request.POST.get('start_date')
        expense.ends_on = request.POST.get('ends_on')
        expense.expense_account = request.POST.get('expense_account')
        expense.expense_type = request.POST.get('expense_type')
        expense.amount = request.POST.get('amount')
        expense.currency = request.POST.get('currency')
        expense.paidthrough = request.POST.get('paidthrough')
        expense.vendor_id = request.POST.get('vendor')
        expense.goods_label = request.POST.get('goods_label')
        expense.gst = request.POST.get('gst')
        expense.destination = request.POST.get('destination')
        expense.tax = request.POST.get('tax')
        expense.notes = request.POST.get('notes')
        customer_id = request.POST.get('customername')  # Get the customer ID from POST data
        customer_obj = get_object_or_404(customer, pk=customer_id)  # Fetch the customer object
        expense.customername = customer_obj.customerName  # Set the customer name in the expense object

        expense.save()
        return redirect('recurringbase')

    else:
        return render(request, 'edit_expense.html', {'expense': expense, 'vendors': vendors, 'customers': customers})    
        
@login_required(login_url='login')
def newexp(request):
    return render(request,'create_expense.html')

def save_data(request):
    if request.method == 'POST':
        account_type = request.POST.get('accountType')
        account_name = request.POST.get('accountName')
        account_code = request.POST.get('accountCode')
        description = request.POST.get('description')

        account = Account(accountType=account_type, accountName=account_name, accountCode=account_code, description=description)
        account.save()

        return redirect('recurringhome')

    return render(request, 'recurring_home.html')   
    
from django.http import JsonResponse
from .models import Account

def get_account_names(request):
    account_names = Account.objects.values_list('accountName', flat=True)
    return JsonResponse(list(account_names), safe=False)
    
@login_required(login_url='login')
def profileshow(request,expense_id):
    expenses = Expense.objects.all()
    expense = get_object_or_404(Expense, id=expense_id)

    return render(request, 'show_recurring.html', {'expenses': expenses,'expense':expense})    
    
def entr_custmr(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            type=request.POST.get('type')
            txtFullName=request.POST['txtFullName']
            cpname=request.POST['cpname']
           
            email=request.POST.get('myEmail')
            wphone=request.POST.get('wphone')
            mobile=request.POST.get('mobile')
            skname=request.POST.get('skname')
            desg=request.POST.get('desg')      
            dept=request.POST.get('dept')
            wbsite=request.POST.get('wbsite')

            gstt=request.POST.get('gstt')
            posply=request.POST.get('posply')
            tax1=request.POST.get('tax1')
            crncy=request.POST.get('crncy')
            obal=request.POST.get('obal')

            select = request.POST.get('pterms')
        try:
            pterms = payment_terms.objects.get(id=select)
        except payment_terms.DoesNotExist:
            pterms = None

            plst=request.POST.get('plst')
            plang=request.POST.get('plang')
            fbk=request.POST.get('fbk')
            twtr=request.POST.get('twtr')
        
            atn=request.POST.get('atn')
            ctry=request.POST.get('ctry')
            
            addrs=request.POST.get('addrs')
            addrs1=request.POST.get('addrs1')
            bct=request.POST.get('bct')
            bst=request.POST.get('bst')
            bzip=request.POST.get('bzip')
            bpon=request.POST.get('bpon')
            bfx=request.POST.get('bfx')

            sal=request.POST.get('sal')
            ftname=request.POST.get('ftname')
            ltname=request.POST.get('ltname')
            mail=request.POST.get('mail')
            bworkpn=request.POST.get('bworkpn')
            bmobile=request.POST.get('bmobile')

            bskype=request.POST.get('bskype')
            bdesg=request.POST.get('bdesg')
            bdept=request.POST.get('bdept')
            u = User.objects.get(id = request.user.id)

          
            ctmr=customer(customerName=txtFullName,customerType=type,
                        companyName=cpname,customerEmail=email,customerWorkPhone=wphone,
                         customerMobile=mobile,skype=skname,designation=desg,department=dept,
                           website=wbsite,GSTTreatment=gstt,placeofsupply=posply, Taxpreference=tax1,
                             currency=crncy,OpeningBalance=obal,PaymentTerms=pterms,
                                PriceList=plst,PortalLanguage=plang,Facebook=fbk,Twitter=twtr,
                                 Attention=atn,country=ctry,Address1=addrs,Address2=addrs1,
                                  city=bct,state=bst,zipcode=bzip,phone1=bpon,
                                   fax=bfx,CPsalutation=sal,Firstname=ftname,
                                    Lastname=ltname,CPemail=mail,CPphone=bworkpn,
                                    CPmobile= bmobile,CPskype=bskype,CPdesignation=bdesg,
                                     CPdepartment=bdept,user=u )
            ctmr.save()  
            
            return redirect("recurringhome")
        return render(request,'recurring_home.html')    
        
from django.http import JsonResponse

def get_customer_names(request):
    customers = customer.objects.all()
    customer_names = [{'id': c.id, 'name': c.customerName} for c in customers]
    return JsonResponse(customer_names, safe=False)    
    
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    return redirect('recurringbase')


def get_profile_details(request, profile_id):
    expense = get_object_or_404(Expense, id=profile_id)
    vendor = expense.vendor 
    data = {
        'id': expense.id,
        'profile_name': expense.profile_name,
        'repeat_every': expense.repeat_every,
        'start_date': expense.start_date,
        'ends_on': expense.ends_on,
        'expense_account': expense.expense_account,
        'expense_type': expense.expense_type,
        'amount': expense.amount,
        'paidthrough': expense.paidthrough,
        'vendor': vendor.vendor_display_name,  
        'gst': expense.gst,
        'destination': expense.destination,
        'tax': expense.tax,
        'notes': expense.notes,
        'customername': expense.customername,
    }
    return JsonResponse(data)    
    
    
@login_required(login_url='login')
def view_sales_order(request):
    sales=SalesOrder.objects.all()
    return render(request,'view_sales_order.html',{"sale":sales})     

    
@login_required(login_url='login')
def create_sales_order(request):
    user = request.user
  
    company = company_details.objects.get(user=user)
    cust=customer.objects.all()
    pay=payment_terms.objects.all()
    itm=AddItem.objects.all()
    context={
        "c":cust,
        "pay":pay,
        "itm":itm,
        "company":company
    }
    return render(request,'create_sales_order.html',context)

    
@login_required(login_url='login')
def add_customer_for_sorder(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            type=request.POST.get('type')
            txtFullName=request.POST['txtFullName']
            cpname=request.POST['cpname']
           
            email=request.POST.get('myEmail')
            wphone=request.POST.get('wphone')
            mobile=request.POST.get('mobile')
            skname=request.POST.get('skname')
            desg=request.POST.get('desg')      
            dept=request.POST.get('dept')
            wbsite=request.POST.get('wbsite')

            gstt=request.POST.get('gstt')
            posply=request.POST.get('posply')
            tax1=request.POST.get('tax1')
            crncy=request.POST.get('crncy')
            obal=request.POST.get('obal')

          
            pterms=request.POST.get('pterms')

            plst=request.POST.get('plst')
            plang=request.POST.get('plang')
            fbk=request.POST.get('fbk')
            twtr=request.POST.get('twtr')
        
            atn=request.POST.get('atn')
            ctry=request.POST.get('ctry')
            
            addrs=request.POST.get('addrs')
            addrs1=request.POST.get('addrs1')
            bct=request.POST.get('bct')
            bst=request.POST.get('bst')
            bzip=request.POST.get('bzip')
            bpon=request.POST.get('bpon')
            bfx=request.POST.get('bfx')

            sal=request.POST.get('sal')
            ftname=request.POST.get('ftname')
            ltname=request.POST.get('ltname')
            mail=request.POST.get('mail')
            bworkpn=request.POST.get('bworkpn')
            bmobile=request.POST.get('bmobile')

            bskype=request.POST.get('bskype')
            bdesg=request.POST.get('bdesg')
            bdept=request.POST.get('bdept')
            u = User.objects.get(id = request.user.id)

          
            ctmr=customer(customerName=txtFullName,customerType=type,
                        companyName=cpname,customerEmail=email,customerWorkPhone=wphone,
                         customerMobile=mobile,skype=skname,designation=desg,department=dept,
                           website=wbsite,GSTTreatment=gstt,placeofsupply=posply, Taxpreference=tax1,
                             currency=crncy,OpeningBalance=obal,PaymentTerms=pterms,
                                PriceList=plst,PortalLanguage=plang,Facebook=fbk,Twitter=twtr,
                                 Attention=atn,country=ctry,Address1=addrs,Address2=addrs1,
                                  city=bct,state=bst,zipcode=bzip,phone1=bpon,
                                   fax=bfx,CPsalutation=sal,Firstname=ftname,
                                    Lastname=ltname,CPemail=mail,CPphone=bworkpn,
                                    CPmobile= bmobile,CPskype=bskype,CPdesignation=bdesg,
                                     CPdepartment=bdept,user=u )
            ctmr.save()  
            
            return redirect("create_sales_order")

    
@login_required(login_url='login')        
def payment_term_for_sorder(request):
    if request.method=='POST':
        term=request.POST.get('term')
        day=request.POST.get('day')
        ptr=payment_terms(Terms=term,Days=day)
        ptr.save()
        return redirect("create_sales_order")
        
        




    
@login_required(login_url='login')
def add_sales_order(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            c=request.POST['cx_name']
            cus=customer.objects.get(customerName=c)   
            custo=cus.id
            sales_no=request.POST['sale_no']
            terms=request.POST['term']
            term=payment_terms.objects.get(id=terms)
            reference=request.POST['ord_no']
            sa_date=request.POST['sa_date']
            sh_date=request.POST['sh_date']
           
      
        
            
            cxnote=request.POST['customer_note']
            subtotal=request.POST['subtotal']
            igst=request.POST['igst']
            cgst=request.POST['cgst']
            sgst=request.POST['sgst']
            totaltax=request.POST['totaltax']
            t_total=request.POST['t_total']
            if request.FILES.get('file') is not None:
                file=request.FILES['file']
            else:
                file="/static/images/alt.jpg"
            tc=request.POST['ter_cond']

            status=request.POST['sd']
            if status=='draft':
                print(status)   
            else:
                print(status)  
        
            product=request.POST.getlist('item[]')
            hsn=request.POST.getlist('hsn[]')
            quantity=request.POST.getlist('quantity[]')
            rate=request.POST.getlist('rate[]')
            desc=request.POST.getlist('desc[]')
            tax=request.POST.getlist('tax[]')
            total=request.POST.getlist('amount[]')
            term=payment_terms.objects.get(id=term.id)

            sales=SalesOrder(customer_id=custo,sales_no=sales_no,terms=term,reference=reference, sales_date=sa_date,ship_date=sh_date,
                        cxnote=cxnote,subtotal=subtotal,igst=igst,cgst=cgst,sgst=sgst,t_tax=totaltax,
                        grandtotal=t_total,status=status,terms_condition=tc,file=file,)
            sales.save()
            sale_id=SalesOrder.objects.get(id=sales.id)
            if len(product)==len(quantity)==len(tax)==len(total)==len(rate):

                mapped = zip(product,quantity,tax,total,rate)
                mapped = list(mapped)
                for element in mapped:
                    created =sales_item.objects.get_or_create(sale=sale_id,product=element[0],
                                        quantity=element[1],tax=element[2],total=element[3],rate=element[4])
                
            return redirect('view_sales_order')    
    
@login_required(login_url='login')
def sales_order_det(request,id):
    sales=SalesOrder.objects.get(id=id)
    saleitem=sales_item.objects.filter(sale_id=id)
    sale_order=SalesOrder.objects.all()
    company=company_details.objects.get(user_id=request.user.id)
    
    
    context={
        'sale':sales,
        'saleitem':saleitem,
        'sale_order':sale_order,
        'comp':company,
        
        
                    }
    return render(request,'sales_order_det.html',context)


    
@login_required(login_url='login')
def delet_sales(request,id):
    d=SalesOrder.objects.get(id=id)
    d.delete()
    return redirect('view_sales_order')
    
    
@login_required(login_url='login')
def edit_sales_order(request,id):
    user = request.user
    company = company_details.objects.get(user=user)
    c = customer.objects.all()
    itm = AddItem.objects.all()
    salesitem = sales_item.objects.filter(sale_id=id)
    sales = SalesOrder.objects.get(id=id)
    pay=payment_terms.objects.all()
    

    if request.method == 'POST':
        u=request.user.id
        c=request.POST['cx_name']
        
        cust=customer.objects.get(customerName=c) 
        sales.customer=cust
        term=request.POST['term']
        
        
        sales.terms = payment_terms.objects.get(id=term)
        sales.sales_date = request.POST['sa_date']
        sales.shipdate=request.POST['sh_date']
        sales.cxnote = request.POST['customer_note']
        sales.igst = request.POST['igst']
        sales.cgst = request.POST['cgst']
        sales.sgst = request.POST['sgst']
        sales.t_tax = request.POST['totaltax']
        sales.grandtotal = request.POST['t_total']

        if request.FILES.get('file') is not None:
            sales.file = request.FILES['file']
        else:
            sales.file = "/static/images/alt.jpg"

            sales.terms_condition = request.POST.get('ter_cond')
        
        status=request.POST['sd']
        if status=='draft':
            sales.status=status      
        else:
            sales.status=status   
         
        sales.save()
        
        product=request.POST.getlist('item[]')
        quantity=request.POST.getlist('quantity[]')
        rate=request.POST.getlist('rate[]')
        tax=request.POST.getlist('tax[]')
        total=request.POST.getlist('amount[]')
        obj_dele=sales_item.objects.filter(sale_id=sales.id)
        obj_dele.delete()
       
        if len(product)==len(quantity)==len(tax)==len(total)==len(rate):

            mapped = zip(product,quantity,tax,total,rate)
            mapped = list(mapped)
            for element in mapped:
                created = sales_item.objects.get_or_create(sale=sales,product=element[0],
                                    quantity=element[1],tax=element[2],total=element[3],rate=element[4])
                
            return redirect('sales_order_det',id)
    context={
        "c":c,
        "itm":itm,
        "saleitm":salesitem,
        "sale":sales,
        "pay":pay,
         "company":company

    }
    return render(request,'edit_sale_page.html',context)
    
    
def create_delivery_chellan(request):
    user = request.user
    # print(user_id)
    company = company_details.objects.get(user=user)
    items = AddItem.objects.filter(user_id=user.id)
    customers = customer.objects.filter(user_id=user.id)
    dates=date.today()
    estimates_count = DeliveryChellan.objects.filter(user_id=user.id).count()
    print(estimates_count)
    next_count = estimates_count+1

    unit=Unit.objects.all()
    sale=Sales.objects.all()
    purchase=Purchase.objects.all()
    accounts = Purchase.objects.all()
    account_types = set(Purchase.objects.values_list('Account_type', flat=True))

    
    account = Sales.objects.all()
    account_type = set(Sales.objects.values_list('Account_type', flat=True))

    context = {'company': company,
               'items': items,
               'customers': customers,
               'count': next_count,
               'date':dates,
               'unit':unit,
               'sale':sale,
               'purchase':purchase,
                "account":account,
                "account_type":account_type,
                "accounts":accounts,
                "account_types":account_types,

               }

    return render(request, 'create_delivery_chellan.html', context)


def delivery_chellan_home(request):
    company = company_details.objects.get(user = request.user)
    viewitem=DeliveryChellan.objects.filter(user=request.user)
    
    return render(request,'delivery_chellan.html',{'view':viewitem,"company":company})  
def create_challan_draft(request):
    
    cur_user = request.user
    user = User.objects.get(id=cur_user.id)
   
    if request.method == 'POST':
        cust_name = request.POST['customer_name']
        chellan_no = request.POST['chellan_number']
        reference = request.POST['reference']
        chellan_date = request.POST['chellan_date']
        customer_mailid = request.POST['customer_mail']
        chellan_type = request.POST['chellan_type']

        item = request.POST.getlist('item[]')
        quantity1 = request.POST.getlist('quantity[]')
        quantity = [float(x) for x in quantity1]
        rate1 = request.POST.getlist('rate[]')
        rate = [float(x) for x in rate1]
        discount1 = request.POST.getlist('discount[]')
        discount = [float(x) for x in discount1]
        tax1 = request.POST.getlist('tax[]')
        tax = [float(x) for x in tax1]
        amount1 = request.POST.getlist('amount[]')
        amount = [float(x) for x in amount1]
       

        cust_note = request.POST['customer_note']
        sub_total = float(request.POST['subtotal'])
        igst = float(request.POST['igst'])
        sgst = float(request.POST['sgst'])
        cgst = float(request.POST['cgst'])
        tax_amnt = float(request.POST['total_taxamount'])
        shipping = float(request.POST['shipping_charge'])
        adjustment = float(request.POST['adjustment_charge'])
        total = float(request.POST['total'])
        tearms_conditions = request.POST['tearms_conditions']
        attachment = request.FILES.get('file')
        status = "Draft"
        tot_in_string = str(total)

        challan = DeliveryChellan(user=user, customer_name=cust_name, chellan_no=chellan_no, reference=reference, chellan_date=chellan_date, customer_mailid=customer_mailid,
                              sub_total=sub_total,igst=igst,sgst=sgst,cgst=cgst,tax_amount=tax_amnt,chellan_type=chellan_type, shipping_charge=shipping,
                             adjustment=adjustment, total=total, status=status, customer_notes=cust_note, terms_conditions=tearms_conditions, 
                             attachment=attachment)
        challan.save()

        if len(item) == len(quantity) == len(rate) == len(discount) == len(tax) == len(amount):
            mapped = zip(item, quantity, rate, discount, tax, amount)
            mapped = list(mapped)
            for element in mapped:
                created = ChallanItems.objects.create(
                    chellan=challan, item_name=element[0], quantity=element[1], rate=element[2], discount=element[3], tax_percentage=element[4], amount=element[5])

        cust_email = customer.objects.get(
            user=user, customerName=cust_name).customerEmail
        
        # subject = 'Estimate'
        # message = 'Dear Customer,\n Your Estimate has been Saved for a total amount of: ' + tot_in_string
        # recipient = cust_email
        # send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient])

    return redirect('delivery_chellan_home')

def create_and_send_challan(request):
    cur_user = request.user
    user = User.objects.get(id=cur_user.id)
    
   
    if request.method == 'POST':
        cust_name = request.POST['customer_name']
        chellan_no = request.POST['chellan_number']
        reference = request.POST['reference']
        chellan_date = request.POST['chellan_date']
        customer_mailid = request.POST['customer_mail']
        chellan_type = request.POST['chellan_type']

        item = request.POST.getlist('item[]')
        quantity1 = request.POST.getlist('quantity[]')
        quantity = [float(x) for x in quantity1]
        rate1 = request.POST.getlist('rate[]')
        rate = [float(x) for x in rate1]
        discount1 = request.POST.getlist('discount[]')
        discount = [float(x) for x in discount1]
        tax1 = request.POST.getlist('tax[]')
        tax = [float(x) for x in tax1]
        amount1 = request.POST.getlist('amount[]')
        amount = [float(x) for x in amount1]
      

        cust_note = request.POST['customer_note']
        sub_total = float(request.POST['subtotal'])
        igst = float(request.POST['igst'])
        sgst = float(request.POST['sgst'])
        cgst = float(request.POST['cgst'])
        tax_amnt = float(request.POST['total_taxamount'])
        shipping = float(request.POST['shipping_charge'])
        adjustment = float(request.POST['adjustment_charge'])
        total = float(request.POST['total'])
        tearms_conditions = request.POST['tearms_conditions']
        attachment = request.FILES.get('file')
        status = 'Send'
        tot_in_string = str(total)

        challan = DeliveryChellan(user=user, customer_name=cust_name, chellan_no=chellan_no, reference=reference, chellan_date=chellan_date, customer_mailid=customer_mailid,
                              sub_total=sub_total,igst=igst,sgst=sgst,cgst=cgst,tax_amount=tax_amnt,chellan_type=chellan_type, shipping_charge=shipping,
                             adjustment=adjustment, total=total, status=status, customer_notes=cust_note, terms_conditions=tearms_conditions, 
                             attachment=attachment)
        challan.save()

        if len(item) == len(quantity) == len(rate) == len(discount) == len(tax) == len(amount):
            mapped = zip(item, quantity, rate, discount, tax, amount)
            mapped = list(mapped)
            for element in mapped:
                created = ChallanItems.objects.create(
                    chellan=challan, item_name=element[0], quantity=element[1], rate=element[2], discount=element[3], tax_percentage=element[4], amount=element[5])

        cust_email = customer.objects.get(
            user=user, customerName=cust_name).customerEmail
      
        subject = 'Delivery Challan'
        message = 'Dear Customer,\n Your Delivery Challan has been Saved for a total amount of: ' + tot_in_string
        recipient = cust_email
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient])

    return redirect('delivery_chellan_home')


def add_customer_for_challan(request):
   
    return render(request,'create_cust_challan.html')
    
def payment_term_challan(request):
    if request.method=='POST':
        term=request.POST.get('term')
        day=request.POST.get('day')
        ptr=payment_terms(Terms=term,Days=day)
        ptr.save()
        return redirect("add_customer_for_challan")

def entr_custmr_for_challan(request):
    print("sdfdsfsds")
    type=request.GET.get('types')
    txtFullName=request.GET.get('txtFullNames')
    cpname=request.GET.get('cpnames')
    email=request.GET.get('email_ids')
    mobile=request.GET.get('mobiles')
    wbsite=request.GET.get('wbsites')
    gstt=request.GET.get('gstts')
    posply=request.GET.get('posplys')
    tax1=request.GET.get('tax1s')
    crncy=request.GET.get('crncys')
    obal=request.GET.get('obals')
    select=request.GET.get('ptermss')
    pterms=request.GET.get('ptermss')
    plst=request.GET.get('plsts')
    plang=request.GET.get('plangs')
    fbk=request.GET.get('fbks')
    twtr=request.GET.get('twtrs')
    atn=request.GET.get('atns')
    ctry=request.GET.get('ctrys')
    addrs=request.GET.get('addrss')
    addrs1=request.GET.get('addrs1s')
    bct=request.GET.get('bcts')
    bst=request.GET.get('bsts')
    bzip=request.GET.get('bzips')
    bpon=request.GET.get('bpons')
    bfx=request.GET.get('bfxs')
    sal=request.GET.get('sals')
    ftname=request.GET.get('ftnames')
    ltname=request.GET.get('ltnames')
    mail=request.GET.get('mails')
    bworkpn=request.GET.get('bworkpns')
    bmobile=request.GET.get('bmobiles')

    bskype=request.GET.get('bskypes')
    bdesg=request.GET.get('bdesgs')
    bdept=request.GET.get('bdepts')
    u = User.objects.get(id = request.user.id)


    ctmr=customer(customerName=txtFullName,customerType=type,
                companyName=cpname,customerEmail=email,
                    customerMobile=mobile,
                    website=wbsite,GSTTreatment=gstt,placeofsupply=posply, Taxpreference=tax1,
                        currency=crncy,OpeningBalance=obal,PaymentTerms=pterms,
                        PriceList=plst,PortalLanguage=plang,Facebook=fbk,Twitter=twtr,
                            Attention=atn,country=ctry,Address1=addrs,Address2=addrs1,
                            city=bct,state=bst,zipcode=bzip,phone1=bpon,
                            fax=bfx,CPsalutation=sal,Firstname=ftname,
                            Lastname=ltname,CPemail=mail,CPphone=bworkpn,
                            CPmobile= bmobile,CPskype=bskype,CPdesignation=bdesg,
                                CPdepartment=bdept,user=u )
    ctmr.save() 
    print(txtFullName)
    return JsonResponse({"status": " not", 'customer': txtFullName, "plos":posply})
        
@login_required(login_url='login')
def additem_page_challan(request):
    unit=Unit.objects.all()
    sale=Sales.objects.all()
    purchase=Purchase.objects.all()
    accounts = Purchase.objects.all()
    account_types = set(Purchase.objects.values_list('Account_type', flat=True))

    
    account = Sales.objects.all()
    account_type = set(Sales.objects.values_list('Account_type', flat=True))
    
    

    return render(request,'additem_challan.html',{'unit':unit,'sale':sale,'purchase':purchase,
               
                            "account":account,"account_type":account_type,"accounts":accounts,"account_types":account_types,
                            
                            })

def additem_challan(request):
    
    radio=request.GET.get('radios')
    inter=request.GET.get('inters')
    intra=request.GET.get('intras')
    type=request.GET.get('types')
    name=request.GET.get('names')
    unit=request.GET.get('units')
    sel_price=request.GET.get('sel_prices')
    sel_acc=request.GET.get('sel_accs')
    s_desc=request.GET.get('s_descs')
    cost_price=request.GET.get('cost_prices')
    cost_acc=request.GET.get('cost_accs')      
    p_desc=request.GET.get('p_descs')
    u=request.user.id
    us=request.user
    history="Created by" + str(us)
    user=User.objects.get(id=u)
    unit=Unit.objects.get(id=unit)
    sel=Sales.objects.get(id=sel_acc)
    cost=Purchase.objects.get(id=cost_acc)
    ad_item=AddItem(type=type,Name=name,p_desc=p_desc,s_desc=s_desc,s_price=sel_price,p_price=cost_price,unit=unit,
                sales=sel,purchase=cost,user=user,creat=history,interstate=inter,intrastate=intra
                    )
    ad_item.save()

    return JsonResponse({"status": " not", 'name': name})

def delivery_challan_view(request, id):
    user = request.user
    company = company_details.objects.get(user=user)
    all_estimates = DeliveryChellan.objects.filter(user=user)
    estimate = DeliveryChellan.objects.get(id=id)
    items = ChallanItems.objects.filter(chellan=estimate)
    print(items)
    context = {
        'company': company,
        'all_estimates':all_estimates,
        'estimate': estimate,
        'items': items,
    }
    return render(request, 'delivery_challan_view.html', context)


# delivery_challan_edit.html

def delivery_challan_edit(request,id):
    user = request.user
    company = company_details.objects.get(user=user)
    customers = customer.objects.filter(user_id=user.id)
    items = AddItem.objects.filter(user_id=user.id)
    estimate = DeliveryChellan.objects.get(id=id)
   
    
    pls= customer.objects.get(customerName=estimate.customer_name)
    
    est_items = ChallanItems.objects.filter(chellan=estimate)

    unit=Unit.objects.all()
    sale=Sales.objects.all()
    purchase=Purchase.objects.all()
    accounts = Purchase.objects.all()
    account_types = set(Purchase.objects.values_list('Account_type', flat=True))

    
    account = Sales.objects.all()
    account_type = set(Sales.objects.values_list('Account_type', flat=True))

    

    context = {
        'company': company,
        'estimate': estimate,
        'customers': customers,
        'items': items,
        'est_items': est_items,
        'unit':unit,
        'sale':sale,
        'purchase':purchase,
        "account":account,
        "account_type":account_type,
        "accounts":accounts,
        "account_types":account_types,
        "pls":pls,
    }
    return render(request, 'delivery_challan_edit.html', context)

def update_challan(request,id):
    cur_user = request.user
    user = User.objects.get(id=cur_user.id)

    if request.method == "POST":
        estimate = DeliveryChellan.objects.get(id=id)
        
        estimate.customer_name = request.POST['customer_name']
        estimate.chellan_no = request.POST['chellan_number']
        estimate.reference = request.POST['reference']
        estimate.chellan_date = request.POST['challan_date']
        estimate.customer_mailid = request.POST['customer_mail']
        estimate.chellan_type = request.POST['chellan_type']
    

        estimate.customer_notes = request.POST['customer_note']
        estimate.sub_total = float(request.POST['subtotal'])
        estimate.tax_amount = float(request.POST['total_taxamount'])
        estimate.shipping_charge = float(request.POST['shipping_charge'])
        estimate.adjustment = float(request.POST['adjustment_charge'])
        estimate.total = float(request.POST['total'])
        estimate.terms_conditions = request.POST['tearms_conditions']
        estimate.status = 'Draft'

        old=estimate.attachment
        new=request.FILES.get('file')
        if old != None and new == None:
            estimate.attachment = old
        else:
            estimate.attachment = new

        estimate.save()

        item = request.POST.getlist('item[]')
        quantity1 = request.POST.getlist('quantity[]')
        quantity = [float(x) for x in quantity1]
        rate1 = request.POST.getlist('rate[]')
        rate = [float(x) for x in rate1]
        discount1 = request.POST.getlist('discount[]')
        discount = [float(x) for x in discount1]
        tax1 = request.POST.getlist('tax[]')
        tax = [float(x) for x in tax1]
        amount1 = request.POST.getlist('amount[]')
        amount = [float(x) for x in amount1]
        # print(item)
        # print(quantity)
        # print(rate)
        # print(discount)
        # print(tax)
        # print(amount)

        objects_to_delete = ChallanItems.objects.filter(chellan=id)
        objects_to_delete.delete()

        
        if len(item) == len(quantity) == len(rate) == len(discount) == len(tax) == len(amount):
            mapped = zip(item, quantity, rate, discount, tax, amount)
            mapped = list(mapped)
            for element in mapped:
                created = ChallanItems.objects.get_or_create(
                    chellan=estimate, item_name=element[0], quantity=element[1], rate=element[2], discount=element[3], tax_percentage=element[4], amount=element[5])
        return redirect('delivery_chellan_home')
    return redirect('delivery_chellan_home')

def get_cust_mail(request):
    cur_user = request.user
    user = User.objects.get(id=cur_user.id)
    company = company_details.objects.get(user=user)
    # print(company.state)
  
    cust = request.GET.get('cust')
    print(cust)


    item = customer.objects.get(customerName=cust, user=user)

    # comp=item.companyName
    # print(comp)
    email = item.customerEmail
    # print(email)

    ads=item.Address1
    # print(site)

    mob=item.customerMobile
    # print(mob)

    
    return JsonResponse({"status": " not", 'email': email,'ads':ads,'mob':mob})
    return redirect('/')
    
def add_customer_edit_challan(request):
   
    return render(request,'create_cust_challan_edit.html')



def payment_term_challan_edit(request):
    if request.method=='POST':
        term=request.POST.get('term')
        day=request.POST.get('day')
        ptr=payment_terms(Terms=term,Days=day)
        ptr.save()
        return redirect("add_customer_edit_challan")

def sv_cust_edit_challan(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            type=request.POST.get('type')
            txtFullName=request.POST['txtFullName']
            cpname=request.POST['cpname']
           
            email=request.POST.get('myEmail')
            wphone=request.POST.get('wphone')
            mobile=request.POST.get('mobile')
            skname=request.POST.get('skname')
            desg=request.POST.get('desg')      
            dept=request.POST.get('dept')
            wbsite=request.POST.get('wbsite')

            gstt=request.POST.get('gstt')
            posply=request.POST.get('posply')
            tax1=request.POST.get('tax1')
            crncy=request.POST.get('crncy')
            obal=request.POST.get('obal')

            select=request.POST.get('pterms')
           
            pterms=request.POST.get('pterms')

            plst=request.POST.get('plst')
            plang=request.POST.get('plang')
            fbk=request.POST.get('fbk')
            twtr=request.POST.get('twtr')
        
            atn=request.POST.get('atn')
            ctry=request.POST.get('ctry')
            
            addrs=request.POST.get('addrs')
            addrs1=request.POST.get('addrs1')
            bct=request.POST.get('bct')
            bst=request.POST.get('bst')
            bzip=request.POST.get('bzip')
            bpon=request.POST.get('bpon')
            bfx=request.POST.get('bfx')

            sal=request.POST.get('sal')
            ftname=request.POST.get('ftname')
            ltname=request.POST.get('ltname')
            mail=request.POST.get('mail')
            bworkpn=request.POST.get('bworkpn')
            bmobile=request.POST.get('bmobile')

            bskype=request.POST.get('bskype')
            bdesg=request.POST.get('bdesg')
            bdept=request.POST.get('bdept')
            u = User.objects.get(id = request.user.id)

          
            ctmr=customer(customerName=txtFullName,customerType=type,
                        companyName=cpname,customerEmail=email,customerWorkPhone=wphone,
                         customerMobile=mobile,skype=skname,designation=desg,department=dept,
                           website=wbsite,GSTTreatment=gstt,placeofsupply=posply, Taxpreference=tax1,
                             currency=crncy,OpeningBalance=obal,PaymentTerms=pterms,
                                PriceList=plst,PortalLanguage=plang,Facebook=fbk,Twitter=twtr,
                                 Attention=atn,country=ctry,Address1=addrs,Address2=addrs1,
                                  city=bct,state=bst,zipcode=bzip,phone1=bpon,
                                   fax=bfx,CPsalutation=sal,Firstname=ftname,
                                    Lastname=ltname,CPemail=mail,CPphone=bworkpn,
                                    CPmobile= bmobile,CPskype=bskype,CPdesignation=bdesg,
                                     CPdepartment=bdept,user=u )
            ctmr.save()  
            
            return redirect("delivery_chellan_home")
        return redirect("delivery_chellan_home")

@login_required(login_url='login')
def additem_edit_challan(request):
    unit=Unit.objects.all()
    sale=Sales.objects.all()
    purchase=Purchase.objects.all()
    accounts = Purchase.objects.all()
    account_types = set(Purchase.objects.values_list('Account_type', flat=True))

    
    account = Sales.objects.all()
    account_type = set(Sales.objects.values_list('Account_type', flat=True))
    
    

    return render(request,'additem_challanedit.html',{'unit':unit,'sale':sale,'purchase':purchase,
               
                            "account":account,"account_type":account_type,"accounts":accounts,"account_types":account_types,
                            
                            })

def additem_challan_edit(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            radio=request.POST.get('radio')
            if radio=='tax':
    
                
                inter=request.POST['inter']
                intra=request.POST['intra']
                type=request.POST.get('type')
                name=request.POST['name']
                unit=request.POST['unit']
                sel_price=request.POST.get('sel_price')
                sel_acc=request.POST.get('sel_acc')
                s_desc=request.POST.get('sel_desc')
                cost_price=request.POST.get('cost_price')
                cost_acc=request.POST.get('cost_acc')      
                p_desc=request.POST.get('cost_desc')
                u=request.user.id
                us=request.user
                history="Created by" + str(us)
                user=User.objects.get(id=u)
                unit=Unit.objects.get(id=unit)
                sel=Sales.objects.get(id=sel_acc)
                cost=Purchase.objects.get(id=cost_acc)
                ad_item=AddItem(type=type,Name=name,p_desc=p_desc,s_desc=s_desc,s_price=sel_price,p_price=cost_price,unit=unit,
                            sales=sel,purchase=cost,user=user,creat=history,interstate=inter,intrastate=intra
                                )
                
            else:
                                                  
                type=request.POST.get('type')
                name=request.POST['name']
                unit=request.POST['unit']
                sel_price=request.POST.get('sel_price')
                sel_acc=request.POST.get('sel_acc')
                s_desc=request.POST.get('sel_desc')
                cost_price=request.POST.get('cost_price')
                cost_acc=request.POST.get('cost_acc')      
                p_desc=request.POST.get('cost_desc')
                u=request.user.id
                us=request.user
                history="Created by" + str(us)
                user=User.objects.get(id=u)
                unit=Unit.objects.get(id=unit)
                sel=Sales.objects.get(id=sel_acc)
                cost=Purchase.objects.get(id=cost_acc)
                ad_item=AddItem(type=type,Name=name,p_desc=p_desc,s_desc=s_desc,s_price=sel_price,p_price=cost_price,unit=unit,
                            sales=sel,purchase=cost,user=user,creat=history,interstate='none',intrastate='none'
                                )
                ad_item.save()
            ad_item.save()
           
            return redirect("delivery_chellan_home")
    return redirect("additem_edit_challan")

@login_required(login_url='login')
def add_account_challan_edit(request):
    print("haii")
    if request.method=='POST':
        Account_type  =request.POST['acc_type']
        Account_name =request.POST['acc_name']
        Acount_code =request.POST['acc_code']
        Account_desc =request.POST['acc_desc']
       
        acc=Purchase(Account_type=Account_type,Account_name=Account_name,Acount_code=Acount_code,Account_desc=Account_desc)
        acc.save()                 
        return redirect("additem_edit_challan")
        
    return redirect("additem_edit_challan")

@login_required(login_url='login')
def add_unit_edit_challan(request):
    if request.method=='POST':
        unit_name=request.POST['unit_name']
        Unit(unit=unit_name).save()
        return redirect('additem_edit_challan')
    return redirect("additem_edit_challan")

@login_required(login_url='login')
def add_sales_edit_challan(request):
    if request.method=='POST':
        Account_type  =request.POST['acc_type']
        Account_name =request.POST['acc_name']
        Acount_code =request.POST['acc_code']
        Account_desc =request.POST['acc_desc']        
        acc=Sales(Account_type=Account_type,Account_name=Account_name,Acount_code=Acount_code,Account_desc=Account_desc)
        acc.save()
        return redirect('additem_edit_challan')
    return redirect("additem_edit_challan")

@login_required(login_url='login')
def add_account_challan(request):
    if request.method=='POST':
        Account_type  =request.POST['acc_type']
        Account_name =request.POST['acc_name']
        Acount_code =request.POST['acc_code']
        Account_desc =request.POST['acc_desc']
       
        acc=Purchase(Account_type=Account_type,Account_name=Account_name,Acount_code=Acount_code,Account_desc=Account_desc)
        acc.save()                 
        return redirect("additem_page_challan")
        
    return redirect("additem_page_challan")

@login_required(login_url='login')
def add_unit_challan(request):
    if request.method=='POST':
        unit_name=request.POST['unit_name']
        Unit(unit=unit_name).save()
        return redirect('additem_page_challan')
    return redirect("additem_page_challan")

@login_required(login_url='login')
def add_sales_challan(request):
    if request.method=='POST':
        Account_type  =request.POST['acc_type']
        Account_name =request.POST['acc_name']
        Acount_code =request.POST['acc_code']
        Account_desc =request.POST['acc_desc']        
        acc=Sales(Account_type=Account_type,Account_name=Account_name,Acount_code=Acount_code,Account_desc=Account_desc)
        acc.save()
        return redirect('additem_page_challan')
    return redirect("additem_page_challan")



def render_challan_pdf(request,id):

    user = request.user
    company = company_details.objects.get(user=user)
    challn_on = DeliveryChellan.objects.filter(user=user)
    challan = DeliveryChellan.objects.get(id=id)
    items = ChallanItems.objects.filter(chellan=challan)
    print(challan.customer_name) 
    print(challan.customer_mailid)
    customers = customer.objects.get(user=user,customerName=challan.customer_name,customerEmail=challan.customer_mailid)



    print(items)
    

    total = challan.total

    template_path = 'delivery_challan_pdf.html'
    context = {
        'company': company,
        'challn_on':challn_on,
        'challan': challan,
        'items': items,
        'customers':customers
    }
    fname=challan.chellan_no
   
    # Create a Django response object, and specify content_type as pdftemp_creditnote
    response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename="certificate.pdf"'
    response['Content-Disposition'] =f'attachment; filename= {fname}.pdf'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    


    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def deletechallan(request,id):
    user = request.user
    company = company_details.objects.get(user=user)
    estimate = DeliveryChellan.objects.get(id=id,user=user)
    items = ChallanItems.objects.filter(chellan=id)
    items.delete()
    estimate.delete()
    return redirect('delivery_chellan_home')
    
def filter_chellan(request):
    if request.method=='POST':
        flter_drop  =request.POST['flter_drop']
        company = company_details.objects.get(user = request.user)
        if flter_drop == "Draft":
            viewitem=DeliveryChellan.objects.filter(user=request.user, status="Draft") 
        elif flter_drop == "Send":
            viewitem=DeliveryChellan.objects.filter(user=request.user, status="Send")
        else:
            viewitem=DeliveryChellan.objects.filter(user=request.user)
        return render(request,'delivery_chellan.html',{'view':viewitem,"company":company})  
    return redirect("delivery_chellan_home") 
    
def filter_chellan_type(request):
    if request.method=='POST':
        flter_drop  =request.POST['flter_tp']
        usr_in  =request.POST['usr_in']
        company = company_details.objects.get(user = request.user)
        if flter_drop == "Customer":
            viewitem=DeliveryChellan.objects.filter(user=request.user, customer_name=usr_in) 
        elif flter_drop == "Date":
            fromdate=datetime.strptime(usr_in, "%d-%m-%Y").date()
            print(fromdate)

            viewitem=DeliveryChellan.objects.filter(user=request.user, chellan_date=fromdate)
        elif flter_drop == "Amount":
            viewitem=DeliveryChellan.objects.filter(user=request.user, total=usr_in)
        else:
            viewitem=DeliveryChellan.objects.filter(user=request.user)
        return render(request,'delivery_chellan.html',{'view':viewitem,"company":company})  
    return redirect("delivery_chellan_home") 
    
    
def itemdata_challan(request):
    cur_user = request.user
    user = User.objects.get(id=cur_user.id)
    company = company_details.objects.get(user=user)
    print(company.state)
    id = request.GET.get('id')
    

    print(id)

    item = AddItem.objects.get(Name=id, user=user)
    name=item.Name
    rate = item.p_price
    place = company.state

    return JsonResponse({"status": " not", 'place': place, 'rate': rate})
    return redirect('/')
    

def payment_term_for_sales(request):
    
    if request.method == 'POST':
        terms = json.loads(request.POST.get('terms', '[]'))
        days = json.loads(request.POST.get('days', '[]'))
        pay_term=terms[0]+" "+days[0]
        if len(terms) == len(days):
            for term, day in zip(terms, days):
                
                created = payment_terms.objects.get_or_create(Terms=term, Days=day)
            return JsonResponse({"message": "success","pay_term":pay_term})
      
    return JsonResponse({"message": "success",})
    
    
def report_page(request):
    return render(request,'reports.html')

def report_recurring_invoice(request):
    return render(request,'report_recurring_invoice.html')
    
def payment_recur(request):
    if request.method=='POST':
        terms=request.POST.get('term')
        day=request.POST.get('day')
        ptr=payments_recur(Terms=terms,Days=day)
        ptr.save()
        return HttpResponse({"message":"success"})
        # return redirect("new_recur")

def create_recur(request):
    user = request.user
    # print(user_id)
    company = company_details.objects.get(user=user)
    item=AddItem.objects.all()
    cus=customer.objects.all()
    pay=payments_recur.objects.all()
    every=repeat_every.objects.all()
    # if not payment.objects.filter(term='net 15').exists(): 
    #    payment(term='net 15',days=15).save()
    # if not payment.objects.filter(term='due end of month').exists():
    #     payment(term='due end of month',days=60).save()
    # elif not  payment.objects.filter(term='net 30').exists():
    #     payment(term='net 30',days=30).save() 
    
    return render(request,'recurpage.html',{'item':item,'cus':cus,'pay':pay,'company':company,'every':every})

def new_recur(request):
    if request.method=='POST':
        custname=request.POST.get('customer')
        pos=request.POST.get('supply')
        e_type=request.POST.get('type')
        profile=request.POST.get('name')
        onumber=request.POST.get('order')
        repeat=request.POST.get('every')
        sdate=request.POST.get('start')
        edate=request.POST.get('end')
        pay=request.POST.get('terms')
        notes=request.POST.get('customer_note')
        terms=request.POST.get('ter_cond')
        sub=request.POST.get('subtotal')
        i=request.POST.get('igst')
        c=request.POST.get('cgst')
        s=request.POST.get('sgst')
        taxamt=request.POST.get('total_taxamount')
        ship=request.POST.get('shipping_charge')
        adj=request.POST.get('adjustment_charge')
        tot=request.POST.get('total')
        items=request.POST.getlist('item[]')
        # print(items)
        quantity1 = request.POST.getlist('quantity[]')
        quantity = [float(x) for x in quantity1]
        # print(quantity)
        rate1 = request.POST.getlist('rate[]')
        rate = [float(x) for x in rate1]
        # print(rate)
        discount1 = request.POST.getlist('discount[]')
        discount = [float(x) for x in discount1]
        # print(discount)
        tax1 = request.POST.getlist('tax[]')
        tax = [float(x) for x in tax1]
        print(tax)
        amount1 = request.POST.getlist('amount[]')
        amount = [float(x) for x in amount1]
        print(amount)
        recur=recurring_invoice(
            cname=custname,
            p_supply=pos,
            entry_type=e_type,
            name=profile,
            order_num=onumber,
            every=repeat,
            start=sdate,
            end=edate,
            terms=pay,
            cust_note=notes,
            conditions=terms,
            sub_total=sub,
            igst=i,
            cgst=c,
            sgst=s,
            tax_amount=taxamt,
            shipping_charge=ship,
            adjustment=adj,
            total=tot,
        )
        recur.save()
        if len(items)==len(quantity)==len(rate)==len(discount)==len(tax)==len(amount):
            print(items)
            print(quantity)
            print(rate)
            print(discount)
            print(tax)
            print(amount)
            mapped1 = zip(items,quantity,rate,discount,tax,amount)
            mapped = list(mapped1)
            for element in mapped:
                created =recur_itemtable.objects.get_or_create(
                    iname=element[0], quantity=element[1], rate=element[2], discount=element[3], tax=element[4], amt=element[5],ri=recur)
        
                
        return redirect('view_recurpage')
    else:
        return render(request,'recurpage.html')





def view_recurpage(request):
    recur=recurring_invoice.objects.all()
    return render(request,'viewrecurpage.html',{'recur':recur})

def viewrecur(request,id):
    cust = customer.objects.filter(user_id=request.user.id)
    company=company_details.objects.get(user_id=request.user.id)
    items=recurring_invoice.objects.all()
    product=recurring_invoice.objects.get(id=id)
    table=recur_itemtable.objects.filter(ri=id)
    print(product.id)
    
    
    context={
        "customer":cust,
       "allproduct":items,
       "product":product,
      "itemstable":table,
      "comp":company,
    }
    
    return render(request,'recur_invoice.html',context)


def edit_recur(request,id):
    item=AddItem.objects.all()
    cus=customer.objects.all()
    editr=recurring_invoice.objects.get(id=id)
    tab=recur_itemtable.objects.filter(ri=id)
    return render(request,'edit_recur.html',{'editr':editr,'cus':cus,'tab':tab,'item':item})

def editrecurpage(request,id):
    if request.method=='POST':
        edit=recurring_invoice.objects.get(id=id)
        edit.p_supply=request.POST['supply']
        edit.entry_type=request.POST['type']
        edit.name=request.POST['name']
        edit.order_num=request.POST['order']
        edit.every=request.POST['every']
        edit.start=request.POST['start']
        edit.end=request.POST['end']
        edit.terms=request.POST['terms']
        edit.cust_note=request.POST['customer_note']
        edit.conditions=request.POST['ter_cond']
        items=request.POST.getlist('item[]')
        # print(items)
        quantity1 = request.POST.getlist('quantity[]')
        quantity = [float(x) for x in quantity1]
        # print(quantity)
        rate1 = request.POST.getlist('rate[]')
        rate = [float(x) for x in rate1]
        # print(rate)
        discount1 = request.POST.getlist('discount[]')
        discount = [float(x) for x in discount1]
        # print(discount)
        tax1 = request.POST.getlist('tax[]')
        tax = [float(x) for x in tax1]
        print(tax)
        amount1 = request.POST.getlist('amount[]')
        amount = [float(x) for x in amount1]
        print(amount)
        sam=recur_itemtable.objects.filter(ri=id).delete()
        if len(items)==len(quantity)==len(rate)==len(discount)==len(tax)==len(amount):
            print(items)
            print(quantity)
            print(rate)
            print(discount)
            print(tax)
            print(amount)
            mapped1 = zip(items,quantity,rate,discount,tax,amount)
            mapped = list(mapped1)
            for element in mapped:
                created =recur_itemtable.objects.get_or_create(
                    iname=element[0], quantity=element[1], rate=element[2], discount=element[3], tax=element[4], amt=element[5],ri=edit)
        edit.save()
        return redirect('view_recurpage')



def del_recur(request,del_id):
    user = request.user
    company = company_details.objects.get(user=user)
    estimate =recurring_invoice.objects.get(id=del_id)
    items =recur_itemtable.objects.filter(ri=estimate)
    items.delete()
    estimate.delete()
    # d=recurring_invoice.objects.get(id=id)
    # # d1=recur_itemtable.objects.get(id=id)
    # d.delete()
    # # d1.delete()
    return redirect('view_recurpage')


    
def itemdata_recur(request):
    cur_user = request.user
    user = User.objects.get(id=cur_user.id)
    company = company_details.objects.get(user=user)
    print(company.state)
    id = request.GET.get('id')
    cust = request.GET.get('cust')
    print(id)
    print(cust)

    item = AddItem.objects.get(Name=id, user=user)

    rate = item.p_price
    place = company.state
    gst = item.intrastate
    igst = item.interstate
    place_of_supply = customer.objects.get(
        customerName=cust, user=user).placeofsupply
    return JsonResponse({"status": " not", 'place': place, 'rate': rate, 'pos': place_of_supply, 'gst': gst, 'igst': igst})
    return redirect('/')

    
@login_required(login_url='login')
def recurring_bill(request):

    company = company_details.objects.get(user = request.user)
    recur = recurring_bills.objects.filter(user = request.user.id)
    context = {
                'company' : company,
                'recur_bill' : recur
            }
    return render(request,'recurring_bills.html',context)

# filter

@login_required(login_url='login')
def recur_custasc(request):
    cmp1 = company_details.objects.get(user = request.user)
    rec_bill =recurring_bills.objects.filter(user = request.user).order_by('customer_name')

    context = {
            'recur_bill':rec_bill,
            'cmp1': cmp1
            }
    return render(request,'recurring_bills.html',context)

@login_required(login_url='login')
def recur_custdesc(request):
    cmp1 = company_details.objects.get(user = request.user)
    rec_bill =recurring_bills.objects.filter(user = request.user).order_by('-customer_name')

    context = {
            'recur_bill':rec_bill,
            'cmp1': cmp1
            }
    return render(request,'recurring_bills.html',context)

@login_required(login_url='login')
def recur_vendorasc(request):
    cmp1 = company_details.objects.get(user = request.user)
    rec_bill =recurring_bills.objects.filter(user = request.user).order_by('vendor_name')

    context = {
            'recur_bill':rec_bill,
            'cmp1': cmp1
            }
    return render(request,'recurring_bills.html',context)

@login_required(login_url='login')
def recur_vendordesc(request):
    cmp1 = company_details.objects.get(user = request.user)
    rec_bill =recurring_bills.objects.filter(user = request.user).order_by('-vendor_name')

    context = {
            'recur_bill':rec_bill,
            'cmp1': cmp1
            }
    return render(request,'recurring_bills.html',context)

@login_required(login_url='login')
def recur_profileasc(request):
    cmp1 = company_details.objects.get(user = request.user)
    rec_bill =recurring_bills.objects.filter(user = request.user).order_by('profile_name')
    print(rec_bill)
    context = {
            'recur_bill':rec_bill,
            'cmp1': cmp1
            }
    return render(request,'recurring_bills.html',context)

@login_required(login_url='login')
def recur_profiledesc(request):
    cmp1 = company_details.objects.get(user = request.user)
    rec_bill =recurring_bills.objects.filter(user = request.user).order_by('-profile_name')

    context = {
            'recur_bill':rec_bill,
            'cmp1': cmp1
            }
    return render(request,'recurring_bills.html',context)

@login_required(login_url='login')
def add_recurring_bills(request):

    company = company_details.objects.get(user = request.user)
    vendor = vendor_table.objects.filter(user = request.user)
    acnt = Account.objects.filter(user = request.user)
    cust = customer.objects.filter(user = request.user)
    item = AddItem.objects.filter(user = request.user)
    payments = payment_terms.objects.filter(user = request.user)
    units = Unit.objects.all()
    sales=Sales.objects.all()
    purchase=Purchase.objects.all()
    sales_type = set(Sales.objects.values_list('Account_type', flat=True))
    purchase_type = set(Purchase.objects.values_list('Account_type', flat=True))
    context = {
                'company' : company,
                'vendor' : vendor,
                'account': acnt,
                'customer' : cust,
                'item' : item,
                'payments' :payments,
                'units' :units,
                'sales' :sales,
                'purchase':purchase,
                'sales_type':sales_type,
                'purchase_type':purchase_type,
            }
    return render(request,'add_recurring_bills.html',context)

@login_required(login_url='login')
def create_recurring_bills(request):

    company = company_details.objects.get(user = request.user)
    if request.method == 'POST':
        vname = request.POST.get('vendor').rsplit(' ', 1)
        cname = request.POST.get('customer').split(" ")[1:]
        cname = " ".join(cname)
        src_supply = request.POST.get('srcofsupply')
        prof = request.POST['prof_name']
        repeat = request.POST['repeat']
        start = request.POST.get('start_date')
        end = None if request.POST.get('end_date') == "" else  request.POST.get('end_date')
        pay_term =request.POST['terms']
        sub_total =request.POST['subtotal']
        sgst=request.POST['sgst']
        cgst=request.POST['cgst']
        igst=request.POST['igst']
        tax = request.POST['igst']
        # print(request.POST['addcharge'])
        shipping_charge=0 if request.POST['addcharge'] == "" else request.POST['addcharge']
        grand_total=request.POST['grand_total']
        note=request.POST['note']

        u = User.objects.get(id = request.user.id)

        bills = recurring_bills(vendor_name=vname[0],profile_name=prof,customer_name = cname,
                    source_supply=src_supply,repeat_every = repeat,start_date = start,end_date = end,
                    payment_terms =pay_term,sub_total=sub_total,sgst=sgst,cgst=cgst,igst=igst,
                    tax_amount=tax,shipping_charge = shipping_charge,
                    grand_total=grand_total,note=note,company=company,user = u,  )
        bills.save()

        r_bill = recurring_bills.objects.get(id=bills.id)

        if len(request.FILES) != 0:
            r_bill.document=request.FILES['file'] 
            r_bill.save()

        items = request.POST.getlist("item[]")
        accounts = request.POST.getlist("account[]")
        quantity = request.POST.getlist("qty[]")
        rate = request.POST.getlist("rate[]")
        tax = request.POST.getlist("tax[]")
        discount = request.POST.get("discount[]", 0)
        amount = request.POST.getlist("amount[]")

        if len(items)==len(accounts)==len(amount) and items and accounts  and amount:
                mapped=zip(items,accounts,quantity,rate,tax,discount,amount)
                mapped=list(mapped)
                for ele in mapped:

                    it = AddItem.objects.get(user = request.user, id = ele[0]).Name
                    try:
                        int(ele[1])
                        ac = Account.objects.get(user = request.user,id = ele[1]).accountName
                        
                    except ValueError:
                        
                        ac = ele[1]
                    
                    created = recurring_bills_items.objects.get_or_create(item = it,account = ac,quantity=ele[2],rate=ele[3],
                    tax=ele[4],discount = ele[5],amount=ele[6],user = u,company = company, recur_bills = r_bill)

        return redirect('recurring_bill')
    return redirect('recurring_bill')



@login_required(login_url='login')
def edit_recurring_bills(request,id):

    company = company_details.objects.get(user = request.user)
    vendor = vendor_table.objects.filter(user = request.user)
    acnt = Account.objects.filter(user = request.user)
    cust = customer.objects.filter(user = request.user)
    item = AddItem.objects.filter(user = request.user)
    payments = payment_terms.objects.filter(user = request.user)
    units = Unit.objects.all()
    sales=Sales.objects.all()
    purchase=Purchase.objects.all()
    sales_type = set(Sales.objects.values_list('Account_type', flat=True))
    purchase_type = set(Purchase.objects.values_list('Account_type', flat=True))
    recur_bills = recurring_bills.objects.get(user = request.user,id=id)
    recur_item = recurring_bills_items.objects.filter(user = request.user,recur_bills = id)    
    c = customer.objects.filter(user = request.user).get(customerName = recur_bills.customer_name)
    v = vendor_table.objects.filter(user = request.user).get(first_name = recur_bills.vendor_name.split(" ")[0], last_name = recur_bills.vendor_name.split(" ")[1])
    # print(recur_bills.vendor_name.split(" "))
    context = {
        'company' : company,
        'vendor' : vendor,
        'account': acnt,
        'customer' : cust,
        'item' : item,
        'payments' :payments,
        'units' :units,
        'sales' :sales,
        'purchase':purchase,
        'sales_type':sales_type,
        'purchase_type':purchase_type,
        'recur_bills': recur_bills,
        'recur_items' : recur_item,
        'cust':c,
        'vend' : v,
    }

    return render(request,'edit_recurring_bills.html',context)


def change_recurring_bills(request,id):
            
    r_bill=recurring_bills.objects.get(user = request.user,id=id)

    if request.method == 'POST':
        
        r_bill.vendor_name = request.POST.get('vendor').rsplit(' ', 1)[0]
        r_bill.customer_name= " ".join(request.POST.get('customer').split(" ")[1:])
        r_bill.profile_name = request.POST['prof_name']
        r_bill.source_supply=request.POST['srcofsupply']
        r_bill.repeat_every=request.POST['repeat']
        r_bill.start_date=request.POST['start_date']
        r_bill.end_date=None if request.POST.get('end_date') == "" else  request.POST.get('end_date')
        r_bill.payment_terms=request.POST['terms']
        r_bill.note=request.POST['note']
        # r_bill.document=request.POST.get('file')
        r_bill.sub_total=None if request.POST.get('subtotal') == "" else  request.POST.get('subtotal')
        r_bill.igst=None if request.POST.get('igst') == "" else  request.POST.get('igst')
        r_bill.cgst=None if request.POST.get('cgst') == "" else  request.POST.get('cgst')
        r_bill.sgst=None if request.POST.get('sgst') == "" else  request.POST.get('sgst')
        r_bill.shipping_charge=request.POST['addcharge']
        r_bill.grand_total=request.POST.get('grand_total')

        if len(request.FILES) != 0:
             
            r_bill.document = request.FILES['file']
            

        r_bill.save()          

        items = request.POST.getlist("item[]")
        account = request.POST.getlist("account[]")
        quantity = request.POST.getlist("quantity[]")
        rate = request.POST.getlist("rate[]")
        tax = request.POST.getlist("tax[]")
        discount = request.POST.get("discount[]", 0)
        amount = request.POST.getlist("amount[]")

        # billid=recurring_bills.objects.get(id=r_bill.id,user = request.user)

        if len(items)==len(account)==len(amount) :
            
            mapped=zip(items,account,quantity,rate,tax,discount,amount)
            mapped=list(mapped)
            
            count = recurring_bills_items.objects.filter(recur_bills=r_bill.id).count()
            
            for ele in mapped:

                if int(len(items))>int(count):

                    pbillss=recurring_bills.objects.get(id=id)
                    company = company_details.objects.get(user = request.user)
                    it = AddItem.objects.get(user = request.user, id = ele[0]).Name
                    it = AddItem.objects.get(user = request.user, id = ele[0]).Name
                    try:
                        int(ele[1])
                        ac = Account.objects.get(user = request.user,id = ele[1]).accountName
                        
                    except ValueError:
                        
                        ac = ele[1]
                    
                    created = recurring_bills_items.objects.get_or_create(item = it,account = ac,quantity=ele[2],rate=ele[3],
                    tax=ele[4],discount = ele[5],amount=ele[6],recur_bills=r_bill.id,company=company,user = request.user)


                else:
                    
                    dbs=recurring_bills_items.objects.get(recur_bills =r_bill.id,item = ele[0],account=ele[1])
                    created = recurring_bills_items.objects.filter(recur_bills =dbs.recur_bills,items = ele[0],account=ele[1]).update(item = ele[0],
                        account = ele[1],quantity=ele[2],rate=ele[3], tax=ele[4],discount=ele[5],amount= ele[6])
 

        return redirect('view_recurring_bills',id)
    return redirect('recurring_bill')


@login_required(login_url='login')
def delete_recurring_bills(request, id):

    company = company_details.objects.get(user = request.user)
    rbill=recurring_bills.objects.get(user = request.user, id= id)
    billitem = recurring_bills_items.objects.filter(user = request.user,recur_bills=id)

    rbill.delete() 
    billitem.delete() 
     
    return redirect('recurring_bill')



    
@login_required(login_url='login')
def view_recurring_bills(request,id):

    company = company_details.objects.get(user = request.user)
    bills = recurring_bills.objects.filter(user = request.user)
    rbill=recurring_bills.objects.get(user = request.user, id= id)
    billitem = recurring_bills_items.objects.filter(user = request.user,recur_bills=id)

    comp_state = company.state
    cust = customer.objects.get(customerName = rbill.customer_name)

    gst_or_igst = "GST" if comp_state == cust.placeofsupply else "IGST"


    tax_total = 0 
    for b in billitem:
        tax_total += b.tax

    context = {
                'company' : company,
                'recur_bills' : bills,
                'recur_bill' : rbill,
                'bill_item' : billitem,
                'tax' : tax_total,
                "gst_or_igst" : gst_or_igst,
                'customer' : cust,
            }

    return render(request, 'view_recurring_bills.html',context)


@login_required(login_url='login')
def view_custasc(request,id):
    company = company_details.objects.get(user = request.user)
    bills =recurring_bills.objects.filter(user = request.user).order_by('customer_name')

    rbill=recurring_bills.objects.get(user = request.user, id= id)
    billitem = recurring_bills_items.objects.filter(user = request.user,recur_bills=id)

    comp_state = company.state
    cust = customer.objects.get(customerName = rbill.customer_name)

    gst_or_igst = "GST" if comp_state == cust.placeofsupply else "IGST"


    tax_total = 0 
    for b in billitem:
        tax_total += b.tax

    context = {
                'company' : company,
                'recur_bills' : bills,
                'recur_bill' : rbill,
                'bill_item' : billitem,
                'tax' : tax_total,
                "gst_or_igst" : gst_or_igst,
                'customer' : cust,
            }
    return render(request,'view_recurring_bills.html',context)

@login_required(login_url='login')
def view_custdesc(request,id):
    company = company_details.objects.get(user = request.user)
    bills =recurring_bills.objects.filter(user = request.user).order_by('-customer_name')

    rbill=recurring_bills.objects.get(user = request.user, id= id)
    billitem = recurring_bills_items.objects.filter(user = request.user,recur_bills=id)

    comp_state = company.state
    cust = customer.objects.get(customerName = rbill.customer_name)

    gst_or_igst = "GST" if comp_state == cust.placeofsupply else "IGST"


    tax_total = 0 
    for b in billitem:
        tax_total += b.tax

    context = {
                'company' : company,
                'recur_bills' : bills,
                'recur_bill' : rbill,
                'bill_item' : billitem,
                'tax' : tax_total,
                "gst_or_igst" : gst_or_igst,
                'customer' : cust,
            }
    return render(request,'view_recurring_bills.html',context)

@login_required(login_url='login')
def view_vendorasc(request,id):
    company = company_details.objects.get(user = request.user)
    bills =recurring_bills.objects.filter(user = request.user).order_by('vendor_name')

    rbill=recurring_bills.objects.get(user = request.user, id= id)
    billitem = recurring_bills_items.objects.filter(user = request.user,recur_bills=id)

    comp_state = company.state
    cust = customer.objects.get(customerName = rbill.customer_name)

    gst_or_igst = "GST" if comp_state == cust.placeofsupply else "IGST"


    tax_total = 0 
    for b in billitem:
        tax_total += b.tax

    context = {
                'company' : company,
                'recur_bills' : bills,
                'recur_bill' : rbill,
                'bill_item' : billitem,
                'tax' : tax_total,
                "gst_or_igst" : gst_or_igst,
                'customer' : cust,
            }
    return render(request,'view_recurring_bills.html',context)

@login_required(login_url='login')
def view_vendordesc(request,id):
    company = company_details.objects.get(user = request.user)
    bills =recurring_bills.objects.filter(user = request.user).order_by('-vendor_name')

    rbill=recurring_bills.objects.get(user = request.user, id= id)
    billitem = recurring_bills_items.objects.filter(user = request.user,recur_bills=id)

    comp_state = company.state
    cust = customer.objects.get(customerName = rbill.customer_name)

    gst_or_igst = "GST" if comp_state == cust.placeofsupply else "IGST"


    tax_total = 0 
    for b in billitem:
        tax_total += b.tax

    context = {
                'company' : company,
                'recur_bills' : bills,
                'recur_bill' : rbill,
                'bill_item' : billitem,
                'tax' : tax_total,
                "gst_or_igst" : gst_or_igst,
                'customer' : cust,
            }
    return render(request,'view_recurring_bills.html',context)

@login_required(login_url='login')
def view_profileasc(request,id):
    company = company_details.objects.get(user = request.user)
    bills =recurring_bills.objects.filter(user = request.user).order_by('profile_name')

    rbill=recurring_bills.objects.get(user = request.user, id= id)
    billitem = recurring_bills_items.objects.filter(user = request.user,recur_bills=id)

    comp_state = company.state
    cust = customer.objects.get(customerName = rbill.customer_name)

    gst_or_igst = "GST" if comp_state == cust.placeofsupply else "IGST"


    tax_total = 0 
    for b in billitem:
        tax_total += b.tax

    context = {
                'company' : company,
                'recur_bills' : bills,
                'recur_bill' : rbill,
                'bill_item' : billitem,
                'tax' : tax_total,
                "gst_or_igst" : gst_or_igst,
                'customer' : cust,
            }
    return render(request,'view_recurring_bills.html',context)

@login_required(login_url='login')
def view_profiledesc(request,id):

    company = company_details.objects.get(user = request.user)
    bills =recurring_bills.objects.filter(user = request.user).order_by('-profile_name')

    rbill=recurring_bills.objects.get(user = request.user, id= id)
    billitem = recurring_bills_items.objects.filter(user = request.user,recur_bills=id)

    comp_state = company.state
    cust = customer.objects.get(customerName = rbill.customer_name)

    gst_or_igst = "GST" if comp_state == cust.placeofsupply else "IGST"


    tax_total = 0 
    for b in billitem:
        tax_total += b.tax

    context = {
                'company' : company,
                'recur_bills' : bills,
                'recur_bill' : rbill,
                'bill_item' : billitem,
                'tax' : tax_total,
                "gst_or_igst" : gst_or_igst,
                'customer' : cust,
            }
    return render(request,'view_recurring_bills.html',context)


@login_required(login_url='login')
def get_vendordet(request):

    company= company_details.objects.get(user = request.user)

    fname = request.POST.get('fname')
    lname = request.POST.get('lname')
    id = request.POST.get('id')
    vdr = vendor_table.objects.get(user=company.user_id,first_name = fname,last_name = lname,id=id)
    vemail = vdr.vendor_email
    gstnum = vdr.gst_number
    gsttr = vdr.gst_treatment

    return JsonResponse({'vendor_email' :vemail, 'gst_number' : gstnum,'gst_treatment':gsttr},safe=False)

@login_required(login_url='login')
def get_customerdet(request):

    company= company_details.objects.get(user = request.user)

    name = request.POST.get('name')
    id = request.POST.get('id')
    # print(name)

    cust = customer.objects.get(user=company.user_id,id = id, customerName=name.strip())
    email = cust.customerEmail
    gstin = 0
    gsttr = cust.GSTTreatment
    cstate = cust.placeofsupply.split("] ")[1:]
    state = 'Not Specified' if cstate == "" else cstate

    return JsonResponse({'customer_email' :email, 'gst_treatment':gsttr, 'gstin': gstin , 'state' : state},safe=False)

@login_required(login_url='login')
def recurbills_vendor(request):
    
    company = company_details.objects.get(user = request.user)

    if request.method=='POST':

        title=request.POST.get('title')
        first_name=request.POST.get('firstname')
        last_name=request.POST.get('lastname')
        comp=request.POST.get('company_name')
        dispn = request.POST.get('display_name')
        email=request.POST.get('email')
        website=request.POST.get('website')
        w_mobile=request.POST.get('work_mobile')
        p_mobile=request.POST.get('pers_mobile')
        skype = request.POST.get('skype')
        desg = request.POST.get('desg')
        dpt = request.POST.get('dpt')
        gsttype=request.POST.get('gsttype')
        gstin=request.POST.get('gstin')
        panno=request.POST.get('panno')
        supply=request.POST.get('sourceofsupply')
        currency=request.POST.get('currency')
        balance=request.POST.get('openingbalance')
        payment=request.POST.get('paymentterms')
        street=request.POST.get('street')
        city=request.POST.get('city')
        state=request.POST.get('state')
        pincode=request.POST.get('pincode')
        country=request.POST.get('country')
        fax=request.POST.get('fax')
        phone=request.POST.get('phone')
        shipstreet=request.POST.get('shipstreet')
        shipcity=request.POST.get('shipcity')
        shipstate=request.POST.get('shipstate')
        shippincode=request.POST.get('shippincode')
        shipcountry=request.POST.get('shipcountry')
        shipfax=request.POST.get('shipfax')
        shipphone=request.POST.get('shipphone')

        u = User.objects.get(id = request.user.id)

        vndr = vendor_table(salutation=title, first_name=first_name, last_name=last_name,vendor_display_name = dispn, company_name= comp, gst_treatment=gsttype, gst_number=gstin, 
                    pan_number=panno,vendor_wphone = w_mobile,vendor_mphone = p_mobile, vendor_email=email,skype_number = skype,
                    source_supply=supply,currency=currency, website=website, designation = desg, department = dpt,
                    opening_bal=balance,baddress=street, bcity=city, bstate=state, payment_terms=payment,bzip=pincode, 
                    bcountry=country, saddress=shipstreet, scity=shipcity, sstate=shipstate,szip=shippincode, scountry=shipcountry,
                    bfax = fax, sfax = shipfax, bphone = phone, sphone = shipphone,user = u)
        vndr.save()

        return HttpResponse({"message": "success"})
        
@login_required(login_url='login')
def vendor_dropdown(request):
    user = User.objects.get(id=request.user.id)

    options = {}
    option_objects = vendor_table.objects.filter(user = user)
    for option in option_objects:
        options[option.id] = [option.salutation, option.first_name, option.last_name, option.id]

    return JsonResponse(options)


@login_required(login_url='login')
def recurbills_pay(request):
    
    company = company_details.objects.get(user = request.user)

    if request.method=='POST':

        name=request.POST.get('name')
        days=request.POST.get('days')
        
        u = User.objects.get(id = request.user.id)

        pay = payment_terms(Terms=name, Days=days, user = u)
        pay.save()

        return HttpResponse({"message": "success"})
        
@login_required(login_url='login')
def pay_dropdown(request):

    user = User.objects.get(id=request.user.id)

    options = {}
    option_objects = payment_terms.objects.filter(user = user)
    for option in option_objects:
        options[option.id] = [option.Terms,option.Days]

    return JsonResponse(options)


@login_required(login_url='login')
def recurbills_unit(request):
    
    company = company_details.objects.get(user = request.user)

    if request.method=='POST':

        unit =request.POST.get('unit')
        
        u = User.objects.get(id = request.user.id)

        unit = Unit(unit= unit)
        unit.save()

        return HttpResponse({"message": "success"})
        
@login_required(login_url='login')
def unit_dropdown(request):

    user = User.objects.get(id=request.user.id)

    options = {}
    option_objects = Unit.objects.all()
    for option in option_objects:
        options[option.id] = [option.unit,option.id]

    return JsonResponse(options)

@login_required(login_url='login')
def recurbills_item(request):

    company = company_details.objects.get(user = request.user)

    if request.method=='POST':
        
        type=request.POST.get('type')
        name=request.POST.get('name')
        ut=request.POST.get('unit')
        inter=request.POST.get('inter')
        intra=request.POST.get('intra')
        sell_price=request.POST.get('sell_price')
        sell_acc=request.POST.get('sell_acc')
        sell_desc=request.POST.get('sell_desc')
        cost_price=request.POST.get('cost_price')
        cost_acc=request.POST.get('cost_acc')      
        cost_desc=request.POST.get('cost_desc')
        
        units=Unit.objects.get(id=ut)
        sel=Sales.objects.get(id=sell_acc)
        cost=Purchase.objects.get(id=cost_acc)

        history="Created by " + str(request.user)

        u  = User.objects.get(id = request.user.id)

        item=AddItem(type=type,Name=name,p_desc=cost_desc,s_desc=sell_desc,s_price=sell_price,p_price=cost_price,
                     user=u ,creat=history,interstate=inter,intrastate=intra,unit = units,sales = sel, purchase = cost)

        item.save()

        return HttpResponse({"message": "success"})
    
    return HttpResponse("Invalid request method.")

        
@login_required(login_url='login')
def item_dropdown(request):

    user = User.objects.get(id=request.user.id)

    options = {}
    option_objects = AddItem.objects.filter(user = request.user)
    for option in option_objects:
        options[option.id] = [option.Name,option.id]

    return JsonResponse(options)

@login_required(login_url='login')
def recurbills_account(request):

    company = company_details.objects.get(user = request.user)


    if request.method=='POST':
        type=request.POST.get('actype')
        name=request.POST['acname']
        u = User.objects.get(id = request.user.id)
        
        acnt=Account(accountType=type,accountName=name,user = u)

        acnt.save()

        return HttpResponse({"message": "success"})
        
@login_required(login_url='login')
def account_dropdown(request):

    user = User.objects.get(id=request.user.id)

    options = {}
    option_objects = Account.objects.filter(user = user)
    for option in option_objects:
        options[option.id] = [option.accountName,option.id]

    return JsonResponse(options)


@login_required(login_url='login')
def get_rate(request):

    user = User.objects.get(id=request.user.id)
    if request.method=='POST':
        id=request.POST.get('id')

        item = AddItem. objects.get( id = id, user = user)
         
        rate = 0 if item.p_price == "" else item.p_price

        return JsonResponse({"rate": rate},safe=False)
    
@login_required(login_url='login')
def get_cust_state(request):

    user = User.objects.get(id=request.user.id)
    if request.method=='POST':

        id=request.POST.get('id')
        cust = customer.objects.get(id = id, user = user)
        cstate = cust.placeofsupply.split("] ")[1]
        state = 'Not Specified' if cstate == "" else cstate

        return JsonResponse({"state": state},safe=False)
    
@login_required(login_url='login')
def export_pdf(request, id):
    company = company_details.objects.get(user=request.user)
    bills = recurring_bills.objects.filter(user=request.user)
    rbill = recurring_bills.objects.get(user=request.user, id=id)
    billitem = recurring_bills_items.objects.filter(user=request.user, recur_bills=id)

    comp_state = company.state
    cust = customer.objects.get(customerName=rbill.customer_name)

    gst_or_igst = "GST" if comp_state == cust.placeofsupply else "IGST"

    tax_total = 0
    for b in billitem:
        tax_total += b.tax

    script_directory = os.path.dirname(os.path.abspath(__file__))
    template_filename = 'view_recurring_bills.html'
    template_path = os.path.join(script_directory, 'templates', template_filename)

    with open(template_path, 'r') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    section = soup.find('div', class_='print-only')
    section_html = section.prettify()
    template = Template(section_html)

    context = {
        'company': company,
        'recur_bills': bills,
        'recur_bill': rbill,
        'bill_item': billitem,
        'tax': tax_total,
        "gst_or_igst": gst_or_igst,
        'customer': cust,
    }
    html = template.render(Context(context))

    fname = rbill.profile_name
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={fname}.pdf'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    
    return response



@login_required(login_url='login')
def recurbill_comment(request):

    company = company_details.objects.get(user = request.user)

    if request.method=='POST':
        id =request.POST.get('id')
        cmnt =request.POST.get('comment')
        
        u = User.objects.get(id = request.user.id)
        r_bill = recurring_bills.objects.get(user = request.user, id = id)
        r_bill.comments = cmnt
        r_bill.save()

        return HttpResponse({"message": "success"})

@login_required(login_url='login')
def recurbill_add_file(request,id):

    company = company_details.objects.get(user = request.user)
    bill = recurring_bills.objects.get(user = request.user,id=id)
    print(bill)

    if request.method == 'POST':

        bill.document=request.POST.get('file')

        if len(request.FILES) != 0:
             
            bill.document = request.FILES['file']

        bill.save()
        return redirect('view_recurring_bills',id)
    

@require_POST
def recurbill_email(request,id):

    company = company_details.objects.get(user = request.user)
    bill = recurring_bills.objects.get(user = request.user,id=id)

    if request.method == 'POST':

        recipient =request.POST.get('recipient')
        sender =request.POST.get('sender')
        sub =request.POST.get('subject')
        message =request.POST.get('message')

    script_directory = os.path.dirname(os.path.abspath(__file__))
    template_filename = 'view_recurring_bills.html'
    template_path = os.path.join(script_directory, 'templates', template_filename)

    with open(template_path, 'r') as file:
        html_content = file.read()
        

    soup = BeautifulSoup(html_content, 'html.parser')
    section = soup.find('div', class_='print-only')
    section_html = section.prettify()
    template = Template(section_html)

    if template:
        prntonly_content = str(template)

    # print(prntonly_content)
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_file:
        temp_file.write(prntonly_content.encode('utf-8'))

    with open(temp_file.name, 'rb') as attachment_file:
        attachment_content = attachment_file.read()

    email = EmailMessage(
        subject=sub,
        body=message,
        from_email=sender,
        to=[recipient],
    )
    email.attach('Recurring Bill',attachment_content , 'text/html')

    email.send()
     
    return HttpResponse(status=200)
    
    
def get_comments(request, profile_name):
    expenses = Expense.objects.filter(profile_name=profile_name)
    comments = [expense.comments for expense in expenses if expense.comments]
    return JsonResponse(comments,safe=False)
    

def every_terms(request):
    if request.method=='POST':
        term=request.POST.get('everyt')
        ptr=repeat_every(Terms=term)
        ptr.save()
        return HttpResponse({"message":"success"})
        
        
def cust_create(request):
    sb=payment_terms.objects.all()
    return render(request,'customer_cr.html',{'sb':sb})
    
def customer_me(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            type=request.POST.get('type')
            txtFullName=request.POST['txtFullName']
            cpname=request.POST['cpname']
           
            email=request.POST.get('email')
            wphone=request.POST.get('fname')
            mobile=request.POST.get('lname')
            skname=request.POST.get('skype')
            desg=request.POST.get('des')      
            dept=request.POST.get('dept')
            wbsite=request.POST.get('wbsite')

            gstt=request.POST.get('gstt')
            posply=request.POST.get('posply')
            tax1=request.POST.get('tax1')
            crncy=request.POST.get('crncy')
            obal=request.POST.get('obal')

            select=request.POST.get('pterms')
            pterms=payment_terms.objects.get(id=select)
            pterms=request.POST.get('pterms')

            plst=request.POST.get('plst')
            plang=request.POST.get('plang')
            fbk=request.POST.get('fbk')
            twtr=request.POST.get('twtr')
        
            atn=request.POST.get('atn')
            ctry=request.POST.get('ctry')
            
            addrs=request.POST.get('addrs')
            addrs1=request.POST.get('addrs1')
            bct=request.POST.get('bct')
            bst=request.POST.get('bst')
            bzip=request.POST.get('bzip')
            bpon=request.POST.get('bpon')
            bfx=request.POST.get('bfx')

            sal=request.POST.get('sal')
            ftname=request.POST.get('ftname')
            ltname=request.POST.get('ltname')
            mail=request.POST.get('mail')
            bworkpn=request.POST.get('bworkpn')
            bmobile=request.POST.get('bmobile')

            bskype=request.POST.get('bskype')
            bdesg=request.POST.get('bdesg')
            bdept=request.POST.get('bdept')
            u = User.objects.get(id = request.user.id)

          
            ctmr=customer(customerName=txtFullName,customerType=type,
                        companyName=cpname,customerEmail=email,customerWorkPhone=wphone,
                         customerMobile=mobile,skype=skname,designation=desg,department=dept,
                           website=wbsite,GSTTreatment=gstt,placeofsupply=posply, Taxpreference=tax1,
                             currency=crncy,OpeningBalance=obal,PaymentTerms=pterms,
                                PriceList=plst,PortalLanguage=plang,Facebook=fbk,Twitter=twtr,
                                 Attention=atn,country=ctry,Address1=addrs,Address2=addrs1,
                                  city=bct,state=bst,zipcode=bzip,phone1=bpon,
                                   fax=bfx,CPsalutation=sal,Firstname=ftname,
                                    Lastname=ltname,CPemail=mail,CPphone=bworkpn,
                                    CPmobile= bmobile,CPskype=bskype,CPdesignation=bdesg,
                                     CPdepartment=bdept,user=u )
            ctmr.save()  
            
            return redirect("/")
        return redirect("/")
        
        
@login_required(login_url='login')
def recurbills_customer(request):
    
    company = company_details.objects.get(user = request.user)

    if request.method=='POST':

        # title=request.POST.get('title')
        # first_name=request.POST.get('firstname')
        # last_name=request.POST.get('lastname')
        # comp=request.POST.get('company_name')
        cust_type = request.POST.get('customer_type')
        name = request.POST.get('display_name')
        comp_name = request.POST.get('company_name')
        email=request.POST.get('email')
        website=request.POST.get('website')
        w_mobile=request.POST.get('work_mobile')
        p_mobile=request.POST.get('pers_mobile')
        fb = request.POST.get('facebook')
        twitter = request.POST.get('twitter')
        skype = request.POST.get('skype')
        desg = request.POST.get('desg')
        dpt = request.POST.get('dpt')
        gsttype=request.POST.get('gsttype')
        # gstin=request.POST.get('gstin')
        # panno=request.POST.get('panno')
        supply=request.POST.get('placeofsupply')
        tax = request.POST.get('tax_preference')
        currency=request.POST.get('currency')
        balance=request.POST.get('openingbalance')
        payment=request.POST.get('paymentterms')
        street1=request.POST.get('street1')
        street2=request.POST.get('street2')
        city=request.POST.get('city')
        state=request.POST.get('state')
        pincode=request.POST.get('pincode')
        country=request.POST.get('country')
        fax=request.POST.get('fax')
        phone=request.POST.get('phone')
        # shipstreet1=request.POST.get('shipstreet1')
        # shipstreet2=request.POST.get('shipstreet2')
        # shipcity=request.POST.get('shipcity')
        # shipstate=request.POST.get('shipstate')
        # shippincode=request.POST.get('shippincode')
        # shipcountry=request.POST.get('shipcountry')
        # shipfax=request.POST.get('shipfax')
        # shipphone=request.POST.get('shipphone')

        u = User.objects.get(id = request.user.id)

        cust = customer(customerName = name,customerType = cust_type, companyName= comp_name, GSTTreatment=gsttype, 
                        customerWorkPhone = w_mobile,customerMobile = p_mobile, customerEmail=email,skype = skype,Facebook = fb, 
                        Twitter = twitter,placeofsupply=supply,Taxpreference = tax,currency=currency, website=website, 
                        designation = desg, department = dpt,OpeningBalance=balance,Address1=street1,Address2=street2, city=city, 
                        state=state, PaymentTerms=payment,zipcode=pincode,country=country,  fax = fax,  phone1 = phone,user = u)
        cust.save()

        return HttpResponse({"message": "success"})
        
        
@login_required(login_url='login')
def customer_dropdown(request):
    user = User.objects.get(id=request.user.id)

    options = {}
    option_objects = customer.objects.filter(user = user)
    for option in option_objects:
        options[option.id] = option.customerName

    return JsonResponse(options)
    
    
def entr_custmrA(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            type=request.POST.get('type')
            txtFullName=request.POST['txtFullName']
            cpname=request.POST['cpname']
           
            email=request.POST.get('email')
            wphone=request.POST.get('wphone')
            mobile=request.POST.get('mobile')
            skname=request.POST.get('skname')
            desg=request.POST.get('desg')      
            dept=request.POST.get('dept')
            wbsite=request.POST.get('wbsite')

            gstt=request.POST.get('v_gsttype')
            gstin=request.POST.get('v_gstin')
            posply=request.POST.get('posply')
            tax1=request.POST.get('tax1')
            crncy=request.POST.get('crncy')
            obal=request.POST.get('obal')

            select=request.POST.get('pterms')
            pterms=payment_terms.objects.get(id=select)
            pterms=request.POST.get('pterms')

            plst=request.POST.get('plst')
            plang=request.POST.get('plang')
            fbk=request.POST.get('fbk')
            twtr=request.POST.get('twtr')
        
            atn=request.POST.get('atn')
            ctry=request.POST.get('ctry')
            
            addrs=request.POST.get('addrs')
            addrs1=request.POST.get('addrs1')
            bct=request.POST.get('bct')
            bst=request.POST.get('bst')
            bzip=request.POST.get('bzip')
            bpon=request.POST.get('bpon')
            bfx=request.POST.get('bfx')

            sal=request.POST.get('sal')
            ftname=request.POST.get('ftname')
            ltname=request.POST.get('ltname')
            mail=request.POST.get('mail')
            bworkpn=request.POST.get('bworkpn')
            bmobile=request.POST.get('bmobile')

            bskype=request.POST.get('bskype')
            bdesg=request.POST.get('bdesg')
            bdept=request.POST.get('bdept')
            u = User.objects.get(id = request.user.id)

          
            ctmr=customer(customerName=txtFullName,
                          customerType=type,
                        companyName=cpname,
                        customerEmail=email,
                        customerWorkPhone=wphone,
                         customerMobile=mobile,skype=skname,
                         designation=desg,department=dept,
                           website=wbsite
                           ,GSTTreatment=gstt,
                           GSTIN=gstin,
                           placeofsupply=posply, Taxpreference=tax1,
                             currency=crncy,OpeningBalance=obal,
                             PaymentTerms=pterms,
                                PriceList=plst,PortalLanguage=plang,
                                Facebook=fbk,
                                Twitter=twtr,
                                 Attention=atn,country=ctry,Address1=addrs,Address=addrs1,
                                  city=bct,state=bst,zipcode=bzip,phone1=bpon,
                                   fax=bfx,CPsalutation=sal,Firstname=ftname,
                                    Lastname=ltname,CPemail=mail,CPphone=bworkpn,
                                    CPmobile= bmobile,CPskype=bskype,CPdesignation=bdesg,
                                     CPdepartment=bdept,user=u )
            ctmr.save()  
            
            return redirect("add_customer")
        return render(request,'customer.html')
def payment_termA(request):
    if request.method=='POST':
        term=request.POST.get('term')
        day=request.POST.get('day')
        ptr=payment_terms(Terms=term,Days=day)
        ptr.save()
        return HttpResponse( {"message":"success"})
        
        
def dashboard(request):
    return render(request,'Dashboard.html')
    
    
def delete_customr(request,id):
    cs=customer.objects.get(id=id)
    cs.delete()
    return redirect('view_customr')
    
def view_customr(request):
    vc=customer.objects.all()
    return render(request,'view_customer.html',{'vc':vc})
    
def view_customr_sname(request):
    vc=customer.objects.order_by('customerName')
    return render(request,'view_customer.html',{'vc':vc})
    
def view_customr_scpname(request):
    vc=customer.objects.order_by('companyName')
    return render(request,'view_customer.html',{'vc':vc})
    
def view_one_customer(request,id):
    vc=customer.objects.all()
    cu=customer.objects.get(id=id)
    return render(request,'view_one_customer.html',{'vc':vc,'cu':cu})
    
def editcustomer(request,id):
    cu=customer.objects.get(id=id)
    pt=payment_terms.objects.all()
  
    return render(request,'edit_customer.html',{'cu':cu,'pt':pt})
    
def editEnter_customer(request,id):
        if request.method=='POST':
            edit=customer.objects.get(id=id)
            edit.customerType=request.POST.get('type')
            edit.customerName=request.POST['txtFullName']
            edit.companyName=request.POST['cpname']

            edit.customerEmail=request.POST['email']
            edit.customerWorkPhone=request.POST['wphone']
            edit.customerMobile=request.POST['mobile']
            edit.skype=request.POST['skname']
            edit.designation=request.POST['desg']
            edit.department=request.POST['dept']
            edit.website=request.POST['wbsite']
            edit.GSTTreatment=request.POST['gstt']
            
            edit.placeofsupply=request.POST['posply']
           
            edit.Taxpreference=request.POST['tax1']
            edit.currency=request.POST['crncy']
            edit.OpeningBalance=request.POST['obal']
            
            edit.PaymentTerms=request.POST['pterms']
            
            edit.PriceList=request.POST['plst']
            edit.PortalLanguage=request.POST['plang']
            edit .Facebook=request.POST['fbk']
            edit.Twitter=request.POST['twtr']
            edit.Attention=request.POST['atn']
            edit.country=request.POST['ctry']

            edit.Address1=request.POST['addrs']
            edit.Address2=request.POST['addrs1']
            edit.city=request.POST['bct']
            edit.state=request.POST['bst']
            edit.zipcode=request.POST['bzip']
            edit.phone1=request.POST['bpon']
            edit.fax=request.POST['bfx']

            edit.CPsalutation=request.POST['sal']
            edit.Firstname=request.POST['ftname']
            edit.Lastname=request.POST['ltname']
            edit.CPemail=request.POST['mail']
            edit.CPphone=request.POST['bworkpn']
            edit.CPmobile=request.POST['bmobile']
            edit.CPskype=request.POST['bskype']

            edit.CPdesignation=request.POST['bdesg'] 
            edit.CPdepartment=request.POST['bdept']
            
           
            edit.save()
            return redirect('view_customr')

        return render(request,'view_customer.html')
        
def add_email_customer(request):
    
    return render(request,'emailcustomer.html')
    
    
def paymentmethod(request):
    paymnt = payment_item.objects.all()
    vendor = vendor_table.objects.all()
    context = {'paymnt':paymnt,'vendor':vendor}
    return render (request,'payment_method.html',context)


def paymentadd_method(request):
    vendors = vendor_table.objects.all()
    context = {'vendors':vendors}
    return render(request,'payment_method_add.html',context)


def payment_add_details(request):
    if request.method == 'POST':
        select = request.POST['select']
        vendor = vendor_table.objects.get(id=select)
        payment_method = request.POST['select1']
        reference = request.POST['reference']
        date = request.POST['date']
        paid = request.POST['select2']
        amount = request.POST['amount']
        email = request.POST['email']
        balance = request.POST['balance']
        difference = request.POST['difference']


        data = payment_item(
            reference=reference,
            payment=payment_method,
            date=date,
            cash=paid,
            amount=amount,
            vendor=vendor,
            email=email,
            balance=balance,
            current_balance=difference,
        )
        data.save()
    return redirect('paymentmethod')

    
def payment_details_view(request, payment_id):
    payment = get_object_or_404(payment_item, pk=payment_id)
    return render(request, 'payment_details.html', {'payment': payment})


def payment_edit(request,pk):
    payment = payment_item.objects.get(id=pk)
    vendor = vendor_table.objects.all()
    return render(request,'payment_details_edit.html',{'payment':payment,'vendor':vendor})


def payment_edit_view(request,pk):
    if request.method == 'POST':
        payment = payment_item.objects.get(id=pk)
       

        payment.payment = request.POST.get('payment')
        payment.reference = request.POST.get('reference')
        select = request.POST.get('select')
        vendor = vendor_table.objects.get(id=select)
        payment.vendor = vendor
        payment.cash = request.POST.get('cash')
        payment.date = request.POST.get('date')
        payment.email = request.POST.get('email')
        payment.balance = request.POST.get('balance')
        payment.current_balance = request.POST.get('current_balance')
        payment.save()
        return redirect('payment_details', payment_id=pk)
    return render(request, 'payment_details_edit.html')
    

#muhammed Ashiq 

def purchase_order(request):
    vendor=vendor_table.objects.all()
    cust=customer.objects.filter(user = request.user)
    payment=payment_terms.objects.all()
    item=AddItem.objects.all()
    account=Account.objects.all()
    unit=Unit.objects.all()
    sales=Sales.objects.all()
    purchase=Purchase.objects.all()
    context={
        'vendor':vendor,
        'customer':cust,
        'payment':payment,
        'item':item,
        'account':account,
        'units':unit,
        'sales':sales,
        'purchase':purchase,
        
    }
        
    return render(request,'create_purchase_order.html',context)



def purchaseView(request):
    purchase_table=Purchase_Order.objects.all()
    purchase_order_table=Purchase_Order_items.objects.all()
    
    context={
        'pt':purchase_table,
        'po_t':purchase_order_table,
    }
    return render(request,'purchase_order.html',context)


@login_required(login_url='login')
def add_vendor(request):
    if request.method=="POST":
        vendor_data=vendor_table()
        vendor_data.salutation=request.POST['salutation']
        vendor_data.first_name=request.POST['first_name']
        vendor_data.last_name=request.POST['last_name']
        vendor_data.company_name=request.POST['company_name']
        vendor_data.vendor_display_name=request.POST['v_display_name']
        vendor_data.vendor_email=request.POST['vendor_email']
        vendor_data.vendor_wphone=request.POST['w_phone']
        vendor_data.vendor_mphone=request.POST['m_phone']
        vendor_data.skype_number=request.POST['skype_number']
        vendor_data.designation=request.POST['designation']
        vendor_data.department=request.POST['department']
        vendor_data.website=request.POST['website']
        vendor_data.gst_treatment=request.POST['gst']

        x=request.POST['gst']
        if x=="Unregistered Business-not Registered under GST":
            vendor_data.pan_number=request.POST['pan_number']
            vendor_data.gst_number="null"
        else:
            vendor_data.gst_number=request.POST['gst_number']
            vendor_data.pan_number=request.POST['pan_number']

        vendor_data.source_supply=request.POST['source_supply']
        vendor_data.currency=request.POST['currency']
        vendor_data.opening_bal=request.POST['opening_bal']
        vendor_data.payment_terms=request.POST['payment_terms']

        user_id=request.user.id
        udata=User.objects.get(id=user_id)
        vendor_data.user=udata
        vendor_data.battention=request.POST['battention']
        vendor_data.bcountry=request.POST['bcountry']
        vendor_data.baddress=request.POST['baddress']
        vendor_data.bcity=request.POST['bcity']
        vendor_data.bstate=request.POST['bstate']
        vendor_data.bzip=request.POST['bzip']
        vendor_data.bphone=request.POST['bphone']
        vendor_data.bfax=request.POST['bfax']

        vendor_data.sattention=request.POST['sattention']
        vendor_data.scountry=request.POST['scountry']
        vendor_data.saddress=request.POST['saddress']
        vendor_data.scity=request.POST['scity']
        vendor_data.sstate=request.POST['sstate']
        vendor_data.szip=request.POST['szip']
        vendor_data.sphone=request.POST['sphone']
        vendor_data.sfax=request.POST['sfax']
        vendor_data.save()
# .......................................................adding to remaks table.....................
        vdata=vendor_table.objects.get(id=vendor_data.id)
        vendor=vdata
        rdata=remarks_table()
        rdata.remarks=request.POST['remark']
        rdata.user=udata
        rdata.vendor=vdata
        rdata.save()


#  ...........................adding multiple rows of table to model  ........................................................       
        salutation =request.POST.getlist('salutation[]')
        first_name =request.POST.getlist('first_name[]')
        last_name =request.POST.getlist('last_name[]')
        email =request.POST.getlist('email[]')
        work_phone =request.POST.getlist('wphone[]')
        mobile =request.POST.getlist('mobile[]')
        skype_number =request.POST.getlist('skype[]')
        designation =request.POST.getlist('designation[]')
        department =request.POST.getlist('department[]') 
        vdata=vendor_table.objects.get(id=vendor_data.id)
        vendor=vdata
       

        if len(salutation)==len(first_name)==len(last_name)==len(email)==len(work_phone)==len(mobile)==len(skype_number)==len(designation)==len(department):
            mapped2=zip(salutation,first_name,last_name,email,work_phone,mobile,skype_number,designation,department)
            mapped2=list(mapped2)
            print(mapped2)
            for ele in mapped2:
                created = contact_person_table.objects.get_or_create(salutation=ele[0],first_name=ele[1],last_name=ele[2],email=ele[3],
                         work_phone=ele[4],mobile=ele[5],skype_number=ele[6],designation=ele[7],department=ele[8],user=udata,vendor=vendor)
        
       
                 
        return redirect('create_purchase_order')




@login_required(login_url='login')
def purchase_vendor(request):
    
    company = company_details.objects.get(user = request.user)

    if request.method=='POST':

        title=request.POST.get('title')
        first_name=request.POST.get('firstname')
        last_name=request.POST.get('lastname')
        comp=request.POST.get('company_name')
        dispn = request.POST.get('display_name')
        email=request.POST.get('email')
        website=request.POST.get('website')
        w_mobile=request.POST.get('work_mobile')
        p_mobile=request.POST.get('pers_mobile')
        skype = request.POST.get('skype')
        desg = request.POST.get('desg')
        dpt = request.POST.get('dpt')
        gsttype=request.POST.get('gsttype')
        gstin=request.POST.get('gstin')
        panno=request.POST.get('panno')
        supply=request.POST.get('sourceofsupply')
        currency=request.POST.get('currency')
        balance=request.POST.get('openingbalance')
        payment=request.POST.get('paymentterms')
        street=request.POST.get('street')
        city=request.POST.get('city')
        state=request.POST.get('state')
        pincode=request.POST.get('pincode')
        country=request.POST.get('country')
        fax=request.POST.get('fax')
        phone=request.POST.get('phone')
        shipstreet=request.POST.get('shipstreet')
        shipcity=request.POST.get('shipcity')
        shipstate=request.POST.get('shipstate')
        shippincode=request.POST.get('shippincode')
        shipcountry=request.POST.get('shipcountry')
        shipfax=request.POST.get('shipfax')
        shipphone=request.POST.get('shipphone')

        u = User.objects.get(id = request.user.id)

        vndr = vendor_table(salutation=title, first_name=first_name, last_name=last_name,vendor_display_name = dispn, company_name= comp, gst_treatment=gsttype, gst_number=gstin, 
                    pan_number=panno,vendor_wphone = w_mobile,vendor_mphone = p_mobile, vendor_email=email,skype_number = skype,
                    source_supply=supply,currency=currency, website=website, designation = desg, department = dpt,
                    opening_bal=balance,baddress=street, bcity=city, bstate=state, payment_terms=payment,bzip=pincode, 
                    bcountry=country, saddress=shipstreet, scity=shipcity, sstate=shipstate,szip=shippincode, scountry=shipcountry,
                    bfax = fax, sfax = shipfax, bphone = phone, sphone = shipphone,user = u)
        vndr.save()

        return HttpResponse({"message": "success"})



@login_required(login_url='login')
def purchase_customer(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            tax=request.POST.get('tax')
            type=request.POST.get('title')
            first=request.POST['firstname']
            last=request.POST['lastname']
            txtFullName= request.POST['display_name']
            
            itemtype=request.POST.get('itemtype')
            cpname=request.POST['company_name']
            
            email=request.POST.get('email')
            wphone=request.POST.get('work_mobile')
            mobile=request.POST.get('pers_mobile')
            skname=request.POST.get('skype')
            desg=request.POST.get('desg')      
            dept=request.POST.get('dpt')
            wbsite=request.POST.get('website')

            gstt=request.POST.get('gsttype')
            posply=request.POST.get('placesupply')
            crncy=request.POST.get('currency')
            obal=request.POST.get('openingbalance')

           
            pterms=request.POST.get('paymentterms')

            plst=request.POST.get('plst')
            plang=request.POST.get('plang')
            fbk=request.POST.get('facebook')
            twtr=request.POST.get('twitter')
        
            ctry=request.POST.get('country')
            
            street=request.POST.get('street')
            shipstate=request.POST.get('shipstate')
            shipcity=request.POST.get('shipcity')
            bzip=request.POST.get('shippincode')
            shipfax=request.POST.get('shipfax')

            sal=request.POST.get('title')
            addres=street +','+ shipcity+',' + shipstate+',' + bzip
            adress2=addres
            u = User.objects.get(id = request.user.id)

            print(tax)
            ctmr=customer(customerName=txtFullName,customerType=itemtype,
                        companyName=cpname,customerEmail=email,customerWorkPhone=wphone,
                         customerMobile=mobile,skype=skname,designation=desg,department=dept,
                           website=wbsite,GSTTreatment=gstt,placeofsupply=posply, Taxpreference=tax,
                             currency=crncy,OpeningBalance=obal,PaymentTerms=pterms,
                                PriceList=plst,PortalLanguage=plang,Facebook=fbk,Twitter=twtr
                                 ,country=ctry,Address1=addres,Address2=adress2,
                                  city=shipcity,state=shipstate,zipcode=bzip,phone1=wphone,
                                   fax=shipfax,CPsalutation=sal,Firstname=first,
                                    Lastname=last,CPemail=email,CPphone=mobile,
                                    CPmobile= wphone,CPskype=skname,CPdesignation=desg,
                                     CPdepartment=dept,user=u )
            ctmr.save()

        return HttpResponse({"message": "success"})

def customer_dropdown(request):
    user = User.objects.get(id=request.user.id)

    options = {}
    option_objects = customer.objects.filter(user = user)
    for option in option_objects:
        options[option.id] = option.customerName

    return JsonResponse(options)
@login_required(login_url='login')
def purchase_pay(request):
    
    company = company_details.objects.get(user = request.user)

    if request.method=='POST':

        name=request.POST.get('name')
        days=request.POST.get('days')
        
        u = User.objects.get(id = request.user.id)

        pay = payment_terms(Terms=name, Days=days, user = u)
        pay.save()

        return HttpResponse({"message": "success"})
@login_required(login_url='login')
def payment_dropdown(request):

    user = User.objects.get(id=request.user.id)

    options = {}
    option_objects = payment_terms.objects.filter(user = user)
    for option in option_objects:
        options[option.id] = option.Terms + str(option.Days)

    return JsonResponse(options)

@login_required(login_url='login')
def customer_det(request):

    company= company_details.objects.get(user = request.user)
    st=company.state
    name = request.POST.get('name')
    print(name)

    vdr = customer.objects.get(user=company.user_id,customerName=name)
    email = vdr.customerEmail
    gstin = 0
    gsttr = vdr.GSTTreatment
    adres=vdr.Address2
    streat=vdr.Address1
    city=vdr.city
    state=vdr.state
    print(email)
    return JsonResponse({'customer_email' :email, 'gst_treatment':gsttr, 'gstin': gstin,'adres':adres,'st':st,'streat':streat,'city':city,'state':state},safe=False)


def itemdata_challan_save(request):
    cur_user = request.user
    user = User.objects.get(id=cur_user.id)
    company = company_details.objects.get(user=user)
    print(company.state)
    id = request.GET.get('id')
    

    

    item = AddItem.objects.get(Name=id, user=user)
    name=item.Name
    rate = item.p_price
    place = company.state

    return JsonResponse({"status": " not", 'place': place, 'rate': rate})
    return redirect('/')


@login_required(login_url='login')
def vendor_det(request):

    company= company_details.objects.get(user = request.user)

    fname = request.POST.get('fname')
    lname = request.POST.get('lname')
    id = request.POST.get('id')
    vdr = vendor_table.objects.get(user=company.user_id,first_name = fname,last_name = lname,id=id)
    vemail = vdr.vendor_email
    gstnum = vdr.gst_number
    gsttr = vdr.gst_treatment
    address=vdr.baddress  + '' + vdr.bcity + ''+vdr.bstate +''+vdr.bzip+''+vdr.bcountry
    print(address)
    return JsonResponse({'vendor_email' :vemail, 'gst_number' : gstnum,'gst_treatment':gsttr,'address':address},safe=False)


@login_required(login_url='login')
def purchase_unit(request):
    
    company = company_details.objects.get(user = request.user)

    if request.method=='POST':

        unit =request.POST.get('unit')
        
        u = User.objects.get(id = request.user.id)

        unit = Unit(unit= unit)
        unit.save()

        return HttpResponse({"message": "success"})
        
@login_required(login_url='login')
def purchase_unit_dropdown(request):

    user = User.objects.get(id=request.user.id)

    options = {}
    option_objects = Unit.objects.all()
    for option in option_objects:
        options[option.id] = option.unit

    return JsonResponse(options)


@login_required(login_url='login')
def purchase_item(request):

    company = company_details.objects.get(user = request.user)

    if request.method=='POST':
        type=request.POST.get('type')
        name=request.POST['name']
        ut=request.POST['unit']
        inter=request.POST['inter']
        intra=request.POST['intra']
        sell_price=request.POST.get('sell_price')
        sell_acc=request.POST.get('sell_acc')
        sell_desc=request.POST.get('sell_desc')
        cost_price=request.POST.get('cost_price')
        cost_acc=request.POST.get('cost_acc')      
        cost_desc=request.POST.get('cost_desc')
        units=Unit.objects.get(id=ut)
        sel=Sales.objects.get(id=sell_acc)
        cost=Purchase.objects.get(id=cost_acc)

        history="Created by " + str(request.user)
        user = User.objects.get(id = request.user.id)

        item=AddItem(type=type,unit=units,sales=sel,purchase=cost,Name=name,p_desc=cost_desc,s_desc=sell_desc,s_price=sell_price,p_price=cost_price,
                    user=user,creat=history,interstate=inter,intrastate=intra)

        item.save()







        return HttpResponse({"message": "success"})
        
@login_required(login_url='login')
def purchase_item_dropdown(request):

    user = User.objects.get(id=request.user.id)

    options = {}
    option_objects = AddItem.objects.all()
    for option in option_objects:
        options[option.id] = option.Name

    return JsonResponse(options)

@login_required(login_url='login')
def purchase_account(request):

    company = company_details.objects.get(user = request.user)


    if request.method=='POST':
        type=request.POST.get('actype')
        name=request.POST['acname']
        u = User.objects.get(id = request.user.id)

        acnt=Account(accountType=type,accountName=name,user = u)

        acnt.save()

        return HttpResponse({"message": "success"})
        
@login_required(login_url='login')
def purchase_account_dropdown(request):

    user = User.objects.get(id=request.user.id)

    options = {}
    option_objects = Account.objects.filter(user = user)
    for option in option_objects:
        options[option.id] = option.accountName

    return JsonResponse(options)



@login_required(login_url='login')
def create_Purchase_order(request):

    company = company_details.objects.get(user = request.user)
    if request.method == 'POST':
        typ=request.POST.get('option')
        vname = request.POST.get('vendor')
        vmail = request.POST.get('email_inp')
        vgst_t = request.POST.get('gst_trt_inp')
        vgst_n = request.POST.get('gstin_inp')
            
        orgname = request.POST.get('orgName')
        org_gst = request.POST.get('gstNumber')
        org_address = request.POST.get('orgAddress')
        org_street = request.POST.get('orgstreet')
        org_city = request.POST.get('orgcity')
        org_state = request.POST.get('orgstate')
            
        cname = request.POST.get('custom')
        cmail = request.POST.get('custMail')
        caddress = request.POST.get('custAddress')
        cstreet = request.POST.get('custstreet')
        ccity = request.POST.get('custcity')
        cstate = request.POST.get('custstate')

        src_supply = request.POST.get('srcofsupply')
        po = request.POST['pur_ord']
        ref = request.POST['ref']
        terms = request.POST['terms']
        start = request.POST.get('start_date')
        end =  request.POST.get('end_date')
        sub_total =request.POST['subtotal']
        sgst=request.POST['sgst']
        cgst=request.POST['cgst']
        igst=request.POST['igst']
        tax = request.POST['total_taxamount']
        shipping_charge= request.POST['shipping_charge']
        grand_total=request.POST['grandtotal']
        note=request.POST['customer_note']
        terms_con = request.POST['tearms_conditions']
        orgMail=request.POST.get('orgMail')
        u = User.objects.get(id = request.user.id)
        print('yes')
        print(typ)
        if typ=='Organization':
           

            purchase = Purchase_Order(vendor_name=vname,
                                    vendor_mail=vmail,
                                    vendor_gst_traet=vgst_t,
                                    vendor_gst_no=vgst_n,
                                    Org_name=orgname,
                                    Org_address=org_address,
                                    Org_gst=org_gst,
                                    Org_street=org_street,
                                    Org_city=org_city,
                                    Org_state=org_state,
                                    Org_mail=orgMail,
                                    Pur_no=po,
                                    ref=ref,
                                    customer_name = '',
                                    customer_mail='',
                                    customer_address='',
                                    customer_street='',
                                    customer_city='',
                                    customer_state='',
                                    source_supply=src_supply,
                                    payment_terms = terms,
                                    Ord_date = start,
                                    exp_date = end,
                                    sub_total=sub_total,
                                    sgst=sgst,
                                    cgst=cgst,
                                    igst=igst,
                                    tax_amount=tax,
                                    shipping_charge = shipping_charge,
                                    grand_total=grand_total,
                                    note=note,
                                    term=terms_con,
                                    company=company,
                                    user = u,typ=typ  )
            purchase.save()

            p_bill = Purchase_Order.objects.get(id=purchase.id)

            if len(request.FILES) != 0:
                p_bill.document=request.FILES['file'] 
                p_bill.save()
                print('save')
        else:
            purchase = Purchase_Order(vendor_name=vname,
                                    vendor_mail=vmail,
                                    vendor_gst_traet=vgst_t,
                                    vendor_gst_no=vgst_n,
                                    customer_name = cname,
                                    customer_mail=cmail,
                                    customer_street=cstreet,
                                    customer_city=ccity,
                                    customer_state=cstate,
                                    Pur_no=po,
                                    ref=ref,
                                    Org_name='',
                                    Org_address='',
                                    Org_gst='',
                                    Org_street='',
                                    Org_city='',
                                    Org_state='',
                                    Org_mail='',
                                    customer_address=caddress,
                                    source_supply=src_supply,
                                    payment_terms = terms,
                                    Ord_date = start,
                                    exp_date = end,
                                    sub_total=sub_total,
                                    sgst=sgst,
                                    cgst=cgst,
                                    igst=igst,
                                    tax_amount=tax,
                                    shipping_charge = shipping_charge,
                                    grand_total=grand_total,
                                    note=note,
                                    term=terms_con,
                                    company=company,
                                    user = u,typ=typ)
            purchase.save()

            p_bill = Purchase_Order.objects.get(id=purchase.id)

    
            if len(request.FILES) != 0:
                p_bill.document=request.FILES['file'] 
                p_bill.save()
                print('save')
        item = request.POST.getlist("item[]")
        accounts = request.POST.getlist("account[]")
        quantity = request.POST.getlist("quantity[]")
        rate = request.POST.getlist("rate[]")
        tax = request.POST.getlist("tax[]")
        discount = request.POST.getlist("discount[]")
        amount = request.POST.getlist("amount[]")
        if len(item)== len(accounts) == len(quantity) == len(rate) == len(discount) == len(tax) == len(amount):
            mapped = zip(item,accounts, quantity, rate,  tax,discount, amount)
            mapped = list(mapped)
            for ele in mapped:
                

                created = Purchase_Order_items.objects.get_or_create(item = ele[0],account = ele[1],quantity=ele[2],rate=ele[3],tax=ele[4],discount = ele[5],amount=ele[6],user = u,company = company, PO = p_bill,)
            
            print('Done')
            return redirect('purchaseView')
    return redirect('purchas_order')

def purchase_delet(request,id):
    po=Purchase_Order.objects.get(id=id)
    po.delete()
    return redirect('purchaseView')

    
def purchase_bill_view(request,id):
    po=Purchase_Order.objects.all()
    po_t=Purchase_Order_items.objects.filter(PO=id)
    po_table=Purchase_Order.objects.get(id=id)
    company=company_details.objects.get(user_id=request.user.id)
    po_item=Purchase_Order.objects.get(id=id)
    context={
        'po':po,
        'pot':po_t,
        'company':company,
        'po_table':po_table,
        'po_item':po_item,
    }
    return render(request, 'purchase_bill_view.html',context)


def EmailAttachementView_purchase(request):

        if request.method == 'POST':
                
            subject =request.POST['subject']
            message = request.POST['message']
            email = request.POST['email']
            files = request.FILES.getlist('attach')

            try:
                mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [email])
                for f in files:
                    mail.attach(f.name, f.read(), f.content_type)
                mail.send()
                return render(request, 'purchasemail.html')
            except:
               return render(request, 'purchasemail.html')

        return render(request, 'purchasemail.html')




def export_purchase_pdf(request,id):

    user = request.user
    company = company_details.objects.get(user=user)
    challn_on = Purchase_Order.objects.filter(user=user)
    challan = Purchase_Order.objects.get(id=id)
    items = Purchase_Order_items.objects.filter(PO=challan)
    print(challan.customer_name) 
    print(challan.customer_name)
    total = challan.grand_total

    template_path = 'pdfchallan.html'
    context = {
        'company': company,
        'pot':challn_on,
        'po_item': challan,
        'po_table': items, 
    }
    fname=challan.Pur_no
   
    # Create a Django response object, and specify content_type as pdftemp_creditnote
    response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename="certificate.pdf"'
    response['Content-Disposition'] =f'attachment; filename= {fname}.pdf'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    


    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def add_comment(request,pk):
    p=Purchase_Order.objects.get(id=pk)
    if request.method=='POST':
        comment=request.POST.get('comment')
        p.comments=comment
        p.save()
    return redirect('purchase_bill_view',pk)

def edit(request,pk):
    vendor=vendor_table.objects.all()
    cust=customer.objects.filter(user = request.user)
    payment=payment_terms.objects.all()
    item=AddItem.objects.all()
    account=Account.objects.all()
    unit=Unit.objects.all()
    sales=Sales.objects.all()
    purchase=Purchase.objects.all()
    po=Purchase_Order.objects.get(id=pk)
    po_tabl=Purchase_Order_items.objects.filter(PO=pk)
    context={
        'vendor':vendor,
        'customer':cust,
        'payment':payment,
        'item':item,
        'account':account,
        'units':unit,
        'sales':sales,
        'purchase':purchase,
        'po':po,        
        'po_table':po_tabl,
    }
    return render(request,'edit_purchase_order.html',context)


def edit_Purchase_order(request,id):

    company = company_details.objects.get(user = request.user)
    po_id=Purchase_Order.objects.get(id=id)
    if request.method == 'POST':
        typ=request.POST['typ']
        print('yes')
        print(typ)
        if typ=='Organization':
            po_id.vendor_name = request.POST.get('vendor')
            po_id.vendor_mail = request.POST.get('email_inp')
            po_id.vendor_gst_traet = request.POST.get('gst_trt_inp')
            po_id.vendor_gst_no = request.POST.get('gstin_inp')
            po_id.typ=typ
            po_id.Org_name = request.POST.get('orgName')
            po_id.Org_address = request.POST.get('gstNumber')
            po_id.Org_gst = request.POST.get('orgAddress')

            po_id.Org_street=request.POST.get('orgstreet')
            po_id.Org_city=request.POST.get('orgcity')
            po_id.Org_state=request.POST.get('orgstate')
            po_id.Org_mail=request.POST.get('orgMail')

            po_id.customer_name = ''
            po_id.customer_mail = ''
            po_id.customer_address = ''
            po_id.customer_street = ''
            po_id.customer_city = ''
            po_id.customer_state = ''
            

            po_id.source_supply = request.POST.get('srcofsupply')
            po_id.Pur_no = request.POST['pur_ord']
            po_id.ref = request.POST['ref']
            po_id.payment_terms = request.POST['terms']
            po_id.Ord_date = request.POST.get('start_date')
            po_id.exp_date =  request.POST.get('end_date')
            po_id.sub_total =request.POST['subtotal']
            po_id.sgst=request.POST['sgst']
            po_id.cgst=request.POST['cgst']
            po_id.igst=request.POST['igst']
            po_id.tax_amount = request.POST['total_taxamount']
            po_id.shipping_charge= request.POST['shipping_charge']
            po_id.grand_total=request.POST['grandtotal']
            po_id.note=request.POST['customer_note']
            po_id.term = request.POST['tearms_conditions']
            u = User.objects.get(id = request.user.id)

            
            po_id.save()

            p_bill = Purchase_Order.objects.get(id=po_id.id)

            if len(request.FILES) != 0:
                p_bill.document=request.FILES['file'] 
                p_bill.save()
                print('save')
        else:
            po_id.vendor_name = request.POST.get('vendor')
            po_id.vendor_mail = request.POST.get('email_inp')
            po_id.vendor_gst_traet = request.POST.get('gst_trt_inp')
            po_id.vendor_gst_no = request.POST.get('gstin_inp')
            po_id.typ=typ
            
            po_id.Org_name = ''
            po_id.Org_address = ''
            po_id.Org_gst = ''
            po_id.Org_street=''
            po_id.Org_city=''
            po_id.Org_state=''
            po_id.Org_mail=''
            po_id.customer_name = request.POST.get('custom')
            po_id.customer_mail = request.POST.get('custMail')
            po_id.customer_address = request.POST.get('custAddress')
            po_id.customer_street = request.POST.get('custstreet')
            po_id.customer_city = request.POST.get('custcity')
            po_id.customer_state = request.POST.get('custstate')

            po_id.source_supply = request.POST.get('srcofsupply')
            po_id.Pur_no = request.POST['pur_ord']
            po_id.ref = request.POST['ref']
            po_id.payment_terms = request.POST['terms']
            po_id.Ord_date = request.POST.get('start_date')
            po_id.exp_date =  request.POST.get('end_date')
            po_id.sub_total =request.POST['subtotal']
            po_id.sgst=request.POST['sgst']
            po_id.cgst=request.POST['cgst']
            po_id.igst=request.POST['igst']
            po_id.tax_amount = request.POST['total_taxamount']
            po_id.shipping_charge= request.POST['shipping_charge']
            po_id.grand_total=request.POST['grandtotal']
            po_id.note=request.POST['customer_note']
            po_id.term = request.POST['tearms_conditions']
            
            u = User.objects.get(id = request.user.id)

            
            po_id.save()

            p_bill = Purchase_Order.objects.get(id=po_id.id)

        if request.FILES.get('file') is not None:
            po_id.file = request.FILES['file']
        else:
            po_id.file = "/static/images/default.jpg"
        po_id.save()
        item = request.POST.getlist("item[]")
        accounts = request.POST.getlist("account[]")
        quantity = request.POST.getlist("quantity[]")
        rate = request.POST.getlist("rate[]")
        tax = request.POST.getlist("tax[]")
        discount = request.POST.getlist("discount[]")
        amount = request.POST.getlist("amount[]")
        obj_dele=Purchase_Order_items.objects.filter(PO=p_bill.id)
        obj_dele.delete()
        if len(item)== len(accounts) == len(quantity) == len(rate) == len(discount) == len(tax) == len(amount):
            mapped = zip(item,accounts, quantity, rate,  tax,discount, amount)
            mapped = list(mapped)
            for ele in mapped:
                

                created = Purchase_Order_items.objects.get_or_create(item = ele[0],account = ele[1],quantity=ele[2],rate=ele[3],tax=ele[4],discount = ele[5],amount=ele[6],user = u,company = company, PO = p_bill,)
            
            print('Done')
            return redirect('purchase_bill_view',id)
    return redirect('purchaseView')

def change_status(request,pk):
    pur=Purchase_Order.objects.get(id=pk)
    pur.status='Approved'
    pur.save()
    return redirect('purchase_bill_view',pk)

def change_status_draft(request,pk):
    pur=Purchase_Order.objects.get(id=pk)
    pur.status='Draft'
    pur.save()
    return redirect('purchase_bill_view',pk)

def draft(request,id):
    po_table=Purchase_Order.objects.all()
    po=Purchase_Order.objects.filter(status='Draft')
    company=company_details.objects.get(user_id=request.user.id)
    po_item=Purchase_Order.objects.get(id=id)
    context={
        'po':po,
        'company':company,
        'po_table':po_table,
        'po_item':po_item,
    }
    return render(request,"purchase_bill_view.html",context)

def Approved(request,id):
    po_table=Purchase_Order.objects.all()
    po=Purchase_Order.objects.filter(status='Approved')
    company=company_details.objects.get(user_id=request.user.id)
    po_item=Purchase_Order.objects.get(id=id)
    context={
        'po':po,
        'company':company,
        'po_table':po_table,
        'po_item':po_item,
    }
    return render(request,"purchase_bill_view.html",context)