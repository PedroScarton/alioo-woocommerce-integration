DELETE wp_wc_product_meta_lookup
FROM wp_wc_product_meta_lookup
LEFT JOIN wp_posts
ON wp_wc_product_meta_lookup.product_id = wp_posts.ID
WHERE wp_posts.ID IS NULL


DELETE wp_postmeta
FROM wp_postmeta
LEFT JOIN wp_posts
ON wp_postmeta.post_id = wp_posts.ID
WHERE wp_posts.ID IS NULL