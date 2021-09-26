**************************************
Example: RGBMaker
**************************************

Example 1
==========

*Making composite image of TGSS - DSS2 Red - NVSS with catalog data from Vizier and 
Spectral Index data from Spidx file* `catalog <http://tgssadr.strw.leidenuniv.nl/doku.php?id=spidx/>`_ -  de Gasperin, Intema & Frail, MNRAS, 474, 5008 (2018).

.. jupyter-execute::

    from rgbmaker.fetch import query
    import pathlib
    position='speca'
    filepath = pathlib.Path('__file__').parent.resolve() /  "../../jupyter-checks/spidx.fits"
    position='speca'
    query(position=position, px=150, kind='plot', annot=0, spidx_file=filepath)



Example 2
==========

.. jupyter-execute::

    from rgbmaker.imgplt import pl_powerlawsi
    S = [424.0, 60.0]
    S_e = [42.6, 2.6]

    pl_powerlawsi(S,S_e)

