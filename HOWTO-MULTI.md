# Howto nup-arranging

We want the dance cards to be double-sided. That gives the following cases.
Cards with 
 - 1 page: 
   - Layout first page on front. 
   - Empty on back
 - 2 pages: 
   - Layout first page on front 
   - Second on back
 - 3 pages: 
   - Layout first page on front of first card, 
   - second page on front of second card, 
   - third page on back of first card. 
   - empty on back of second card.
 - ...

Generic: 
 - a dance with n pages needs to be layouted on `ceil(n/2)` cards.
 - Given that there a `ceil(n/2)` cards. The target sides are 
   1. front 1
   2. front ...
   3. front n
   4. back 1
   5. back ...
   6. back n

# Steps:
1. Compile single-pdfs
2. Get page numbers from single pdfs
3. Concat page numbers to whole document page numbers <br>*(we need to have all pages in one document since pdfpages (latex package for nupping) only supports a single source document)*
4. Arrange the dances according to page count
5. write the tex file
6. compile tex file