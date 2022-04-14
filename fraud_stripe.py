#setup stripe
import stripe
stripe.api_key = "STRIPE KEY HERE"

#Lists for searching
spacelist=[]
checkedSpaces=[]
checkedPrints=[]
fingerprintlist=[]
finaldict={}


def initsearch():
    # Takes a cc fingerprint via input
    firstprint=input("First fingerprint")
    # Create a querystring and search stripe for that query
    initquery = "payment_method_details.card.fingerprint:'"+firstprint+"'"
    firstList = stripe.Charge.search(query=initquery)
    #paginate the Stripe object returned from query and append every SPACE associated with the FINGERPRINT provided
    for space in firstList.auto_paging_iter():
        if space.metadata.Space not in spacelist:
            spacelist.append(space.metadata.Space)
    #Call next function and pass a list of spaces
    fPrintRetriever(spacelist)

def fPrintRetriever(Spaces):
    # For each space in our SpaceList
    for space in Spaces:
        # Ensure the space has not been checked, then add it to our CHECKED spaces list
        if space not in checkedSpaces:
            checkedSpaces.append(space)

            # Build a new querystring that searches for the SPACE by metadata
            query = "metadata['Space']:'" + space + "'"
            printsRetrieved = stripe.Charge.search(query=str(query))

            # add the space to our final dictionary and build an empty list
            finaldict[space] = []

            # for each charge in the space, paginate over the object and retrieve the CC fingerprint
            for fPrint in printsRetrieved.auto_paging_iter():
                curPrint = fPrint.payment_method_details.card.fingerprint

                # if the fingerprint is not associated to the space, associate it via our dictionary, AND add it to our FINGERPRINT list
                if curPrint not in finaldict[space]:
                    fingerprintlist.append(curPrint)
                    finaldict[space].append(curPrint)

    # if our FINGERPRINT list is longer than our CHECKED fingerprints, we have more fingerprints to search
    if len(fingerprintlist) >len(checkedPrints):
        spaceRetriever(fingerprintlist)

def spaceRetriever(fPrintList):

    # For each FINGERPRINT in our list, ensure we have not checked that fingerprint
    for fPrint in fPrintList:
        if fPrint not in checkedPrints:

            # Add the fingerprint to our CHECKED list
            checkedPrints.append(fPrint)

            # Build a new querystring to search the fingerprints
            printQuery = "payment_method_details.card.fingerprint:'"+fPrint+"'"
            spacesRetrieved = stripe.Charge.search(query=str(printQuery))

            # For each charge associated with that fingerprint, paginate over the object and retrieve the SPACE metadata
            for space in spacesRetrieved.auto_paging_iter():

                # IF the space metadata is not in our SPACE list, add it
                if space.metadata.Space not in spacelist:
                    spacelist.append(space.metadata.Space)

    #IF our space list is longer than our CHECKED spaces list, we have more searches to make
    if len(spacelist)>len(checkedSpaces):
        fPrintRetriever(spacelist)

# Starts our initial search and prints the final dictionary when we exhaust all SPACES and FINGERPRINTS associated with the origin FINGERPRINT
initsearch()
print(finaldict)
