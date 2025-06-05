def texas_hybrid_score(z_dense, z_sparse, lmbda):
	sim_dense_dict = {}
	dense_max_score = max([doc.score for doc in z_dense['retriever_with_embeddings']['documents']])
	for doc in z_dense['retriever_with_embeddings']['documents']:
		if doc.id not in sim_dense_dict:
			sim_dense_dict[doc.id] = doc.score / dense_max_score

	sim_sparse_dict = {}
	sparse_max_score = max([doc.score for doc in z_sparse['retriever']['documents']])
	for doc in z_sparse['retriever']['documents']:
		sim_sparse_dict[doc.id] = doc.score / sparse_max_score

	all_docs = set(sim_dense_dict.keys()).union(sim_sparse_dict.keys())

	s_hybrid = {}
	for doc in all_docs:
		if doc in sim_dense_dict and doc in sim_sparse_dict:
			s_hybrid[doc] = (lmbda*sim_dense_dict[doc] + (1-lmbda)*sim_sparse_dict[doc])
		elif doc in sim_dense_dict:
			s_hybrid[doc] = lmbda*sim_dense_dict[doc]
		else:
			s_hybrid[doc] = (1-lmbda)*sim_sparse_dict[doc]

	s_hybrid_sort = dict(sorted(s_hybrid.items(), key=lambda item: item[1], reverse=True))
	return s_hybrid_sort